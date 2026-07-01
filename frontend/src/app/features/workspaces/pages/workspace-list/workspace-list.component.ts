import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { EmptyStateComponent } from '@shared/components/empty-state/empty-state.component';
import { TimeAgoPipe } from '@shared/pipes/time-ago.pipe';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';
import { NotificationService } from '@core/services/notification.service';
import { Workspace } from '@models/workspace.model';
import { WorkspaceApiService } from '../../services/workspace-api.service';
import { WorkspaceFormDialogComponent } from '../../components/workspace-form-dialog/workspace-form-dialog.component';

@Component({
  selector: 'app-workspace-list',
  standalone: true,
  imports: [CommonModule, EmptyStateComponent, TimeAgoPipe, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './workspace-list.component.html',
  styleUrl: './workspace-list.component.scss',
})
export class WorkspaceListComponent implements OnInit {
  private readonly api = inject(WorkspaceApiService);
  private readonly dialog = inject(MatDialog);
  private readonly router = inject(Router);
  private readonly notify = inject(NotificationService);

  readonly workspaces = signal<Workspace[]>([]);
  readonly loading = signal(true);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api.list().subscribe({
      next: (res) => {
        this.workspaces.set(res.items);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  open(workspace: Workspace): void {
    void this.router.navigate(['/workspaces', workspace.id, 'dashboard']);
  }

  create(): void {
    this.dialog
      .open(WorkspaceFormDialogComponent)
      .afterClosed()
      .subscribe((ws?: Workspace) => {
        if (ws) {
          this.notify.success('Workspace created.');
          this.workspaces.update((list) => [ws, ...list]);
        }
      });
  }

  edit(workspace: Workspace, event: MouseEvent): void {
    event.stopPropagation();
    this.dialog
      .open(WorkspaceFormDialogComponent, { data: { workspace } })
      .afterClosed()
      .subscribe((updated?: Workspace) => {
        if (updated) {
          this.notify.success('Workspace updated.');
          this.workspaces.update((list) =>
            list.map((w) => (w.id === updated.id ? updated : w)),
          );
        }
      });
  }

  remove(workspace: Workspace, event: MouseEvent): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete workspace',
          message: `Delete "${workspace.name}" and all its documents and chats? This cannot be undone.`,
          confirmText: 'Delete',
          destructive: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (confirmed) {
          this.api.delete(workspace.id).subscribe(() => {
            this.notify.success('Workspace deleted.');
            this.workspaces.update((list) =>
              list.filter((w) => w.id !== workspace.id),
            );
          });
        }
      });
  }
}
