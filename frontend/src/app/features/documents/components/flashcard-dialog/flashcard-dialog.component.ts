import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { Flashcard } from '@models/document.model';
import { DocumentApiService } from '../../services/document-api.service';

@Component({
  selector: 'app-flashcard-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './flashcard-dialog.component.html',
  styleUrl: './flashcard-dialog.component.scss',
})
export class FlashcardDialogComponent {
  private readonly api = inject(DocumentApiService);
  readonly data = inject<{ documentId: string; title: string }>(MAT_DIALOG_DATA);

  readonly counts = [5, 10, 20];
  readonly numCards = signal(10);
  readonly generating = signal(false);
  readonly cards = signal<Flashcard[]>([]);
  readonly index = signal(0);
  readonly flipped = signal(false);

  readonly current = computed<Flashcard | undefined>(
    () => this.cards()[this.index()],
  );

  generate(): void {
    if (this.generating()) {
      return;
    }
    this.generating.set(true);
    this.cards.set([]);
    this.index.set(0);
    this.flipped.set(false);
    this.api
      .generateFlashcards(this.data.documentId, this.numCards())
      .subscribe({
        next: (res) => {
          this.cards.set(res.cards);
          this.generating.set(false);
        },
        error: () => this.generating.set(false),
      });
  }

  flip(): void {
    this.flipped.update((v) => !v);
  }

  next(): void {
    if (this.index() < this.cards().length - 1) {
      this.index.update((i) => i + 1);
      this.flipped.set(false);
    }
  }

  prev(): void {
    if (this.index() > 0) {
      this.index.update((i) => i - 1);
      this.flipped.set(false);
    }
  }
}
