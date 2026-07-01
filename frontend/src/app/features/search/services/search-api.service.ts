import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { PageResponse } from '@interfaces/api-response.interface';
import { SearchRequest, SearchResponse } from '@models/search.model';
import { DocumentItem } from '@models/document.model';
import { Chat } from '@models/chat.model';

@Injectable({ providedIn: 'root' })
export class SearchApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  semanticSearch(
    workspaceId: string,
    payload: SearchRequest,
  ): Observable<SearchResponse> {
    return this.http.post<SearchResponse>(
      `${this.baseUrl}/workspaces/${workspaceId}/search`,
      payload,
    );
  }

  searchDocuments(
    workspaceId: string,
    q: string,
  ): Observable<PageResponse<DocumentItem>> {
    const params = new HttpParams().set('q', q).set('size', 50);
    return this.http.get<PageResponse<DocumentItem>>(
      `${this.baseUrl}/workspaces/${workspaceId}/search/documents`,
      { params },
    );
  }

  searchChats(workspaceId: string, q: string): Observable<PageResponse<Chat>> {
    const params = new HttpParams().set('q', q).set('size', 50);
    return this.http.get<PageResponse<Chat>>(
      `${this.baseUrl}/workspaces/${workspaceId}/search/chats`,
      { params },
    );
  }
}
