import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  input,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { EmptyStateComponent } from '@shared/components/empty-state/empty-state.component';
import { Chat, ChatMessage } from '@models/chat.model';
import { ChatApiService } from '../../services/chat-api.service';

@Component({
  selector: 'app-chat-view',
  standalone: true,
  imports: [CommonModule, FormsModule, EmptyStateComponent, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './chat-view.component.html',
  styleUrl: './chat-view.component.scss',
})
export class ChatViewComponent implements OnInit {
  readonly workspaceId = input.required<string>();

  private readonly api = inject(ChatApiService);

  readonly chats = signal<Chat[]>([]);
  readonly activeChatId = signal<string | null>(null);
  readonly messages = signal<ChatMessage[]>([]);
  readonly prompt = signal('');
  readonly sending = signal(false);

  ngOnInit(): void {
    this.loadChats();
  }

  loadChats(): void {
    this.api.listChats(this.workspaceId()).subscribe((res) => {
      this.chats.set(res.items);
      if (res.items.length && !this.activeChatId()) {
        this.selectChat(res.items[0]);
      }
    });
  }

  newChat(): void {
    this.api.createChat(this.workspaceId()).subscribe((chat) => {
      this.chats.update((list) => [chat, ...list]);
      this.activeChatId.set(chat.id);
      this.messages.set([]);
    });
  }

  selectChat(chat: Chat): void {
    this.activeChatId.set(chat.id);
    this.api.listMessages(chat.id).subscribe((res) => this.messages.set(res.items));
  }

  send(): void {
    const text = this.prompt().trim();
    const chatId = this.activeChatId();
    if (!text || !chatId || this.sending()) {
      return;
    }
    const now = new Date().toISOString();
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      chat_id: chatId,
      role: 'user',
      content: text,
      model_name: null,
      latency_ms: null,
      sources: [],
      created_at: now,
    };

    // Placeholder assistant message that fills in as tokens stream.
    const assistantId = crypto.randomUUID();
    const assistant: ChatMessage = {
      id: assistantId,
      chat_id: chatId,
      role: 'assistant',
      content: '',
      model_name: null,
      latency_ms: null,
      sources: [],
      created_at: now,
    };

    this.messages.update((list) => [...list, userMessage, assistant]);
    this.prompt.set('');
    this.sending.set(true);

    void this.api.streamMessage(
      chatId,
      { content: text, top_k: 5 },
      {
        onSources: (sources) => this.patch(assistantId, { sources }),
        onToken: (token) =>
          this.patch(assistantId, {
            content: this.messageById(assistantId)?.content + token,
          }),
        onDone: (messageId, latencyMs) => {
          this.patch(assistantId, { id: messageId, latency_ms: latencyMs });
          this.sending.set(false);
        },
        onError: (detail) => {
          this.patch(assistantId, {
            content: this.messageById(assistantId)?.content || `⚠ ${detail}`,
          });
          this.sending.set(false);
        },
      },
    );
  }

  private messageById(id: string): ChatMessage | undefined {
    return this.messages().find((m) => m.id === id);
  }

  private patch(id: string, changes: Partial<ChatMessage>): void {
    this.messages.update((list) =>
      list.map((m) => (m.id === id ? { ...m, ...changes } : m)),
    );
  }

  activeChat(): Chat | undefined {
    return this.chats().find((c) => c.id === this.activeChatId());
  }
}
