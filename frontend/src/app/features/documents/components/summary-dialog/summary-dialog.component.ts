import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { Summary, SummaryType } from '@models/document.model';
import { DocumentApiService } from '../../services/document-api.service';

interface SummaryTab {
  type: SummaryType;
  label: string;
  icon: string;
  hint: string;
}

@Component({
  selector: 'app-summary-dialog',
  standalone: true,
  imports: [CommonModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './summary-dialog.component.html',
  styleUrl: './summary-dialog.component.scss',
})
export class SummaryDialogComponent implements OnInit {
  private readonly api = inject(DocumentApiService);
  readonly data = inject<{ documentId: string; title: string }>(MAT_DIALOG_DATA);

  readonly tabs: SummaryTab[] = [
    { type: 'short', label: 'Short', icon: 'short_text', hint: '2-3 sentence overview' },
    {
      type: 'detailed',
      label: 'Detailed',
      icon: 'subject',
      hint: 'Comprehensive multi-paragraph summary',
    },
    {
      type: 'executive',
      label: 'Executive',
      icon: 'business_center',
      hint: 'Key findings, risks, and recommended actions',
    },
  ];

  readonly summaries = signal<Record<string, Summary>>({});
  readonly generating = signal<SummaryType | null>(null);

  ngOnInit(): void {
    this.api.listSummaries(this.data.documentId).subscribe((list) => {
      const map: Record<string, Summary> = {};
      for (const s of list) {
        map[s.summary_type] = s;
      }
      this.summaries.set(map);
    });
  }

  content(type: SummaryType): Summary | undefined {
    return this.summaries()[type];
  }

  generate(type: SummaryType): void {
    if (this.generating()) {
      return;
    }
    this.generating.set(type);
    this.api.generateSummary(this.data.documentId, type).subscribe({
      next: (summary) => {
        this.summaries.update((map) => ({ ...map, [type]: summary }));
        this.generating.set(null);
      },
      error: () => this.generating.set(null),
    });
  }
}
