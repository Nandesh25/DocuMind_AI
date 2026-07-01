import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { PageResponse } from '@interfaces/api-response.interface';
import { Chat, ChatMessage, MessageSource, SendMessageRequest } from '@models/chat.model';
import { TokenService } from '@core/services/token.service';

export interface StreamHandlers {
  onSources?: (sources: MessageSource[]) => void;
  onToken?: (token: string) => void;
  onDone?: (messageId: string, latencyMs: number) => void;
  onError?: (detail: string) => void;
}

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly http = inject(HttpClient);
  private readonly tokens = inject(TokenService);
  private readonly baseUrl = environment.apiUrl;

  listChats(workspaceId: string): Observable<PageResponse<Chat>> {
    const params = new HttpParams().set('page', 1).set('size', 50);
    return this.http.get<PageResponse<Chat>>(
      `${this.baseUrl}/workspaces/${workspaceId}/chats`,
      { params },
    );
  }

  createChat(workspaceId: string, title?: string): Observable<Chat> {
    return this.http.post<Chat>(
      `${this.baseUrl}/workspaces/${workspaceId}/chats`,
      { title: title ?? null },
    );
  }

  listMessages(chatId: string): Observable<PageResponse<ChatMessage>> {
    const params = new HttpParams().set('page', 1).set('size', 100);
    return this.http.get<PageResponse<ChatMessage>>(
      `${this.baseUrl}/chats/${chatId}/messages`,
      { params },
    );
  }

  sendMessage(
    chatId: string,
    payload: SendMessageRequest,
  ): Observable<ChatMessage> {
    return this.http.post<ChatMessage>(
      `${this.baseUrl}/chats/${chatId}/messages`,
      payload,
    );
  }

  /**
   * Stream a RAG answer token-by-token over Server-Sent Events. Uses the Fetch
   * API because HttpClient/EventSource cannot POST an SSE request.
   */
  async streamMessage(
    chatId: string,
    payload: SendMessageRequest,
    handlers: StreamHandlers,
    signal?: AbortSignal,
  ): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.tokens.getAccessToken() ?? ''}`,
        },
        body: JSON.stringify(payload),
        signal,
      },
    );

    if (!response.ok || !response.body) {
      let detail = 'Failed to start the response stream.';
      try {
        detail = (await response.json())?.detail ?? detail;
      } catch {
        /* ignore parse errors */
      }
      handlers.onError?.(detail);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      buffer += decoder.decode(value, { stream: true });

      let boundary: number;
      while ((boundary = buffer.indexOf('\n\n')) !== -1) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        this.dispatchFrame(frame, handlers);
      }
    }
  }

  private dispatchFrame(frame: string, handlers: StreamHandlers): void {
    let event = 'message';
    let data = '';
    for (const line of frame.split('\n')) {
      if (line.startsWith('event:')) {
        event = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        data += line.slice(5).trim();
      }
    }
    if (!data) {
      return;
    }
    const payload = JSON.parse(data);
    switch (event) {
      case 'sources':
        handlers.onSources?.(payload.sources ?? []);
        break;
      case 'token':
        handlers.onToken?.(payload.content ?? '');
        break;
      case 'done':
        handlers.onDone?.(payload.message_id, payload.latency_ms);
        break;
      case 'error':
        handlers.onError?.(payload.detail ?? 'Streaming error.');
        break;
    }
  }

  deleteChat(chatId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/chats/${chatId}`);
  }
}
