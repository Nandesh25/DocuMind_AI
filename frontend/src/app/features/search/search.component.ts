import {
  ChangeDetectionStrategy,
  Component,
  inject,
  input,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { EmptyStateComponent } from '@shared/components/empty-state/empty-state.component';
import { TimeAgoPipe } from '@shared/pipes/time-ago.pipe';
import { SearchResult } from '@models/search.model';
import { DocumentItem } from '@models/document.model';
import { Chat } from '@models/chat.model';
import { SearchApiService } from './services/search-api.service';

type SearchMode = 'semantic' | 'documents' | 'chats';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    EmptyStateComponent,
    TimeAgoPipe,
    ...MATERIAL_IMPORTS,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss',
})
export class SearchComponent {
  readonly workspaceId = input.required<string>();

  private readonly api = inject(SearchApiService);
  private readonly router = inject(Router);

  readonly mode = signal<SearchMode>('semantic');
  readonly query = signal('');
  readonly minScore = signal(0.3);

  readonly results = signal<SearchResult[]>([]);
  readonly documents = signal<DocumentItem[]>([]);
  readonly chats = signal<Chat[]>([]);

  readonly searched = signal(false);
  readonly loading = signal(false);

  setMode(mode: SearchMode): void {
    this.mode.set(mode);
    this.searched.set(false);
    this.results.set([]);
    this.documents.set([]);
    this.chats.set([]);
  }

  search(): void {
    const q = this.query().trim();
    if (!q || this.loading()) {
      return;
    }
    this.loading.set(true);
    const ws = this.workspaceId();

    if (this.mode() === 'semantic') {
      this.api
        .semanticSearch(ws, { query: q, top_k: 10, min_score: this.minScore() })
        .subscribe({
          next: (res) => this.finish(() => this.results.set(res.results)),
          error: () => this.loading.set(false),
        });
    } else if (this.mode() === 'documents') {
      this.api.searchDocuments(ws, q).subscribe({
        next: (res) => this.finish(() => this.documents.set(res.items)),
        error: () => this.loading.set(false),
      });
    } else {
      this.api.searchChats(ws, q).subscribe({
        next: (res) => this.finish(() => this.chats.set(res.items)),
        error: () => this.loading.set(false),
      });
    }
  }

  openChat(): void {
    void this.router.navigate(['/workspaces', this.workspaceId(), 'chat']);
  }

  openDocuments(): void {
    void this.router.navigate(['/workspaces', this.workspaceId(), 'documents']);
  }

  private finish(apply: () => void): void {
    apply();
    this.searched.set(true);
    this.loading.set(false);
  }
}
