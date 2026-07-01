import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { Workspace } from '@models/workspace.model';
import { WorkspaceApiService } from '../../services/workspace-api.service';

export interface WorkspaceFormData {
  workspace?: Workspace;
}

@Component({
  selector: 'app-workspace-form-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2 mat-dialog-title>{{ isEdit ? 'Edit workspace' : 'New workspace' }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="dialog-form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Name</mat-label>
          <input matInput formControlName="name" cdkFocusInitial />
          @if (form.controls.name.hasError('minlength')) {
            <mat-error>Name must be at least 2 characters.</mat-error>
          }
        </mat-form-field>
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Description (optional)</mat-label>
          <textarea matInput formControlName="description" rows="3"></textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="dialogRef.close()">Cancel</button>
      <button
        mat-flat-button
        color="primary"
        [disabled]="form.invalid || saving()"
        (click)="save()"
      >
        {{ isEdit ? 'Save' : 'Create' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .dialog-form {
        display: flex;
        flex-direction: column;
        min-width: 360px;
        padding-top: 8px;
      }
    `,
  ],
})
export class WorkspaceFormDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(WorkspaceApiService);
  readonly dialogRef = inject(MatDialogRef<WorkspaceFormDialogComponent>);
  private readonly data = inject<WorkspaceFormData>(MAT_DIALOG_DATA, {
    optional: true,
  });

  readonly isEdit = !!this.data?.workspace;
  readonly saving = signal(false);

  readonly form = this.fb.nonNullable.group({
    name: [
      this.data?.workspace?.name ?? '',
      [Validators.required, Validators.minLength(2)],
    ],
    description: [this.data?.workspace?.description ?? ''],
  });

  save(): void {
    if (this.form.invalid) {
      return;
    }
    this.saving.set(true);
    const payload = this.form.getRawValue();
    const request$ = this.isEdit
      ? this.api.update(this.data!.workspace!.id, payload)
      : this.api.create(payload);

    request$.subscribe({
      next: (ws) => this.dialogRef.close(ws),
      error: () => this.saving.set(false),
    });
  }
}
