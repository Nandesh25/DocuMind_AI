import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  MAT_DIALOG_DATA,
  MatDialogRef,
} from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { FileSizePipe } from '@shared/pipes/file-size.pipe';
import { NotificationService } from '@core/services/notification.service';
import { DocumentApiService } from '../../services/document-api.service';

const ACCEPTED = ['.pdf', '.docx', '.txt', '.md', '.markdown'];

@Component({
  selector: 'app-upload-dialog',
  standalone: true,
  imports: [CommonModule, FileSizePipe, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './upload-dialog.component.html',
  styleUrl: './upload-dialog.component.scss',
})
export class UploadDialogComponent {
  private readonly api = inject(DocumentApiService);
  private readonly notify = inject(NotificationService);
  readonly dialogRef = inject(MatDialogRef<UploadDialogComponent>);
  readonly data = inject<{ workspaceId: string }>(MAT_DIALOG_DATA);

  readonly accept = ACCEPTED.join(',');
  readonly selectedFile = signal<File | null>(null);
  readonly uploading = signal(false);
  readonly dragActive = signal(false);

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragActive.set(true);
  }

  onDragLeave(): void {
    this.dragActive.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragActive.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      this.setFile(file);
    }
  }

  onSelect(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.setFile(file);
    }
  }

  clear(): void {
    this.selectedFile.set(null);
  }

  upload(): void {
    const file = this.selectedFile();
    if (!file || this.uploading()) {
      return;
    }
    this.uploading.set(true);
    this.api.upload(this.data.workspaceId, file).subscribe({
      next: (doc) => {
        this.notify.success('Upload accepted — processing started.');
        this.dialogRef.close(doc);
      },
      error: () => this.uploading.set(false),
    });
  }

  private setFile(file: File): void {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ACCEPTED.includes(ext)) {
      this.notify.error(`Unsupported file type. Allowed: ${ACCEPTED.join(', ')}`);
      return;
    }
    this.selectedFile.set(file);
  }
}
