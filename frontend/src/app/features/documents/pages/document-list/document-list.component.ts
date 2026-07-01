import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  input,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { FileSizePipe } from '@shared/pipes/file-size.pipe';
import { TimeAgoPipe } from '@shared/pipes/time-ago.pipe';
import { EmptyStateComponent } from '@shared/components/empty-state/empty-state.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';
import { NotificationService } from '@core/services/notification.service';
import { DocumentItem, DocumentStatus } from '@models/document.model';
import { DocumentApiService } from '../../services/document-api.service';
import { UploadDialogComponent } from '../../components/upload-dialog/upload-dialog.component';
import { SummaryDialogComponent } from '../../components/summary-dialog/summary-dialog.component';
import { CompareDialogComponent } from '../../components/compare-dialog/compare-dialog.component';
import { QuizDialogComponent } from '../../components/quiz-dialog/quiz-dialog.component';
import { FlashcardDialogComponent } from '../../components/flashcard-dialog/flashcard-dialog.component';

@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [
    CommonModule,
    FileSizePipe,
    TimeAgoPipe,
    EmptyStateComponent,
    ...MATERIAL_IMPORTS,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './document-list.component.html',
  styleUrl: './document-list.component.scss',
})
export class DocumentListComponent implements OnInit {
  readonly workspaceId = input.required<string>();

  private readonly api = inject(DocumentApiService);
  private readonly dialog = inject(MatDialog);
  private readonly notify = inject(NotificationService);

  readonly documents = signal<DocumentItem[]>([]);
  readonly loading = signal(true);
  readonly statusFilter = signal<DocumentStatus | ''>('');
  readonly search = signal('');

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api
      .list(
        this.workspaceId(),
        1,
        50,
        this.statusFilter() || undefined,
        this.search() || undefined,
      )
      .subscribe({
        next: (res) => {
          this.documents.set(res.items);
          this.loading.set(false);
        },
        error: () => this.loading.set(false),
      });
  }

  onStatusChange(value: DocumentStatus | ''): void {
    this.statusFilter.set(value);
    this.load();
  }

  onSearch(value: string): void {
    this.search.set(value);
    this.load();
  }

  upload(): void {
    this.dialog
      .open(UploadDialogComponent, { data: { workspaceId: this.workspaceId() } })
      .afterClosed()
      .subscribe((doc?: DocumentItem) => {
        if (doc) {
          this.documents.update((list) => [doc, ...list]);
        }
      });
  }

  reindex(doc: DocumentItem): void {
    this.api.reindex(doc.id).subscribe((updated) => {
      this.notify.info('Re-indexing started.');
      this.replace(updated);
    });
  }

  download(doc: DocumentItem): void {
    window.open(this.api.downloadUrl(doc.id), '_blank');
  }

  summarize(doc: DocumentItem): void {
    this.dialog.open(SummaryDialogComponent, {
      data: { documentId: doc.id, title: doc.title },
      width: '600px',
    });
  }

  quiz(doc: DocumentItem): void {
    this.dialog.open(QuizDialogComponent, {
      data: { documentId: doc.id, title: doc.title },
      width: '680px',
    });
  }

  flashcards(doc: DocumentItem): void {
    this.dialog.open(FlashcardDialogComponent, {
      data: { documentId: doc.id, title: doc.title },
      width: '560px',
    });
  }

  indexedDocuments(): DocumentItem[] {
    return this.documents().filter((d) => d.status === 'indexed');
  }

  compare(): void {
    const indexed = this.indexedDocuments();
    if (indexed.length < 2) {
      this.notify.info('You need at least two indexed documents to compare.');
      return;
    }
    this.dialog.open(CompareDialogComponent, {
      data: { workspaceId: this.workspaceId(), documents: indexed },
      width: '640px',
    });
  }

  remove(doc: DocumentItem): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete document',
          message: `Delete "${doc.title}"? This removes its indexed data too.`,
          confirmText: 'Delete',
          destructive: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (confirmed) {
          this.api.delete(doc.id).subscribe(() => {
            this.notify.success('Document deleted.');
            this.documents.update((list) => list.filter((d) => d.id !== doc.id));
          });
        }
      });
  }

  statusColor(status: DocumentStatus): string {
    switch (status) {
      case 'indexed':
        return 'primary';
      case 'failed':
        return 'warn';
      default:
        return 'accent';
    }
  }

  private replace(updated: DocumentItem): void {
    this.documents.update((list) =>
      list.map((d) => (d.id === updated.id ? updated : d)),
    );
  }
}
