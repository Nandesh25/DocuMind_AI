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
import { QuizQuestion, QuizType } from '@models/document.model';
import { DocumentApiService } from '../../services/document-api.service';

@Component({
  selector: 'app-quiz-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './quiz-dialog.component.html',
  styleUrl: './quiz-dialog.component.scss',
})
export class QuizDialogComponent {
  private readonly api = inject(DocumentApiService);
  readonly data = inject<{ documentId: string; title: string }>(MAT_DIALOG_DATA);

  readonly types: { value: QuizType; label: string; icon: string }[] = [
    { value: 'mcq', label: 'Multiple Choice', icon: 'list' },
    { value: 'true_false', label: 'True / False', icon: 'rule' },
    { value: 'short', label: 'Short Answer', icon: 'short_text' },
  ];
  readonly counts = [3, 5, 10];

  readonly quizType = signal<QuizType>('mcq');
  readonly numQuestions = signal(5);
  readonly generating = signal(false);
  readonly questions = signal<QuizQuestion[]>([]);
  readonly selected = signal<Record<number, string>>({});
  readonly revealed = signal<Record<number, boolean>>({});

  generate(): void {
    if (this.generating()) {
      return;
    }
    this.generating.set(true);
    this.questions.set([]);
    this.selected.set({});
    this.revealed.set({});
    this.api
      .generateQuiz(this.data.documentId, this.quizType(), this.numQuestions())
      .subscribe({
        next: (res) => {
          this.questions.set(res.questions);
          this.generating.set(false);
        },
        error: () => this.generating.set(false),
      });
  }

  choose(index: number, option: string): void {
    if (this.revealed()[index]) {
      return;
    }
    this.selected.update((m) => ({ ...m, [index]: option }));
  }

  reveal(index: number): void {
    this.revealed.update((m) => ({ ...m, [index]: true }));
  }

  optionClass(index: number, option: string, answer: string): string {
    if (!this.revealed()[index]) {
      return this.selected()[index] === option ? 'selected' : '';
    }
    if (this.matches(option, answer)) {
      return 'correct';
    }
    if (this.selected()[index] === option) {
      return 'incorrect';
    }
    return '';
  }

  private matches(a: string, b: string): boolean {
    return a.trim().toLowerCase() === b.trim().toLowerCase();
  }
}
