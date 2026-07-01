import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  input,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { TimeAgoPipe } from '@shared/pipes/time-ago.pipe';
import { DocumentItem } from '@models/document.model';
import { Chat } from '@models/chat.model';
import { DocumentApiService } from '@features/documents/services/document-api.service';
import { ChatApiService } from '@features/chat/services/chat-api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, TimeAgoPipe, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  readonly workspaceId = input.required<string>();

  private readonly documentApi = inject(DocumentApiService);
  private readonly chatApi = inject(ChatApiService);

  readonly documents = signal<DocumentItem[]>([]);
  readonly chats = signal<Chat[]>([]);
  readonly totalDocuments = signal(0);
  readonly loading = signal(true);

  ngOnInit(): void {
    forkJoin({
      docs: this.documentApi.list(this.workspaceId(), 1, 5),
      chats: this.chatApi.listChats(this.workspaceId()),
    }).subscribe({
      next: ({ docs, chats }) => {
        this.documents.set(docs.items);
        this.totalDocuments.set(docs.total);
        this.chats.set(chats.items.slice(0, 5));
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  indexedCount(): number {
    return this.documents().filter((d) => d.status === 'indexed').length;
  }

  processingCount(): number {
    return this.documents().filter((d) => d.status === 'processing').length;
  }
}
