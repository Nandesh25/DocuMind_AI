import { Routes } from '@angular/router';

import { authGuard } from '@core/guards/auth.guard';
import { guestGuard } from '@core/guards/guest.guard';
import { MainLayoutComponent } from '@core/layout/main-layout/main-layout.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'workspaces' },
  {
    path: 'auth',
    canActivate: [guestGuard],
    loadChildren: () =>
      import('@features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'workspaces',
        loadChildren: () =>
          import('@features/workspaces/workspaces.routes').then(
            (m) => m.WORKSPACE_ROUTES,
          ),
      },
      {
        path: 'workspaces/:workspaceId/dashboard',
        loadComponent: () =>
          import('@features/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent,
          ),
      },
      {
        path: 'workspaces/:workspaceId/documents',
        loadChildren: () =>
          import('@features/documents/documents.routes').then(
            (m) => m.DOCUMENT_ROUTES,
          ),
      },
      {
        path: 'workspaces/:workspaceId/chat',
        loadChildren: () =>
          import('@features/chat/chat.routes').then((m) => m.CHAT_ROUTES),
      },
      {
        path: 'workspaces/:workspaceId/search',
        loadComponent: () =>
          import('@features/search/search.component').then(
            (m) => m.SearchComponent,
          ),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('@features/settings/settings.component').then(
            (m) => m.SettingsComponent,
          ),
      },
    ],
  },
  { path: '**', redirectTo: 'workspaces' },
];
