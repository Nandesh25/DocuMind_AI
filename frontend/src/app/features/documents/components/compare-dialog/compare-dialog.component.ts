import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { NotificationService } from '@core/services/notification.service';
import { ComparisonResult, DocumentItem } from '@models/document.model';
import { DocumentApiService } from '../../services/document-api.service';

@Component({
  selector: 'app-compare-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './compare-dialog.component.html',
  styleUrl: './compare-dialog.component.scss',
})
export class CompareDialogComponent {
  private readonly api = inject(DocumentApiService);
  private readonly notify = inject(NotificationService);
  readonly data = inject<{ workspaceId: string; documents: DocumentItem[] }>(
    MAT_DIALOG_DATA,
  );

  readonly docA = signal<string | null>(null);
  readonly docB = signal<string | null>(null);
  readonly comparing = signal(false);
  readonly result = signal<ComparisonResult | null>(null);

  compare(): void {
    const a = this.docA();
    const b = this.docB();
    if (!a || !b) {
      return;
    }
    if (a === b) {
      this.notify.error('Please select two different documents.');
      return;
    }
    this.comparing.set(true);
    this.result.set(null);
    this.api.compare(this.data.workspaceId, a, b).subscribe({
      next: (res) => {
        this.result.set(res);
        this.comparing.set(false);
      },
      error: () => this.comparing.set(false),
    });
  }

  scorePercent(): number {
    return Math.round((this.result()?.similarity_score ?? 0) * 100);
  }
}
