import { Routes } from '@angular/router';

export const WORKSPACE_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/workspace-list/workspace-list.component').then(
        (m) => m.WorkspaceListComponent,
      ),
  },
];
