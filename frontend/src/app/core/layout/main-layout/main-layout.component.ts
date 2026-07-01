import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  NavigationEnd,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';
import { filter } from 'rxjs';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { AuthService } from '@core/services/auth.service';
import { ThemeService } from '@core/services/theme.service';
import { LoadingService } from '@core/services/loading.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    ...MATERIAL_IMPORTS,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss',
})
export class MainLayoutComponent implements OnInit {
  private readonly router = inject(Router);
  readonly auth = inject(AuthService);
  readonly theme = inject(ThemeService);
  readonly loading = inject(LoadingService);

  readonly workspaceId = signal<string | null>(null);

  ngOnInit(): void {
    this.auth.loadCurrentUser().subscribe();
    this.syncWorkspaceId(this.router.url);
    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((e) => this.syncWorkspaceId(e.urlAfterRedirects));
  }

  logout(): void {
    this.auth.logout();
  }

  private syncWorkspaceId(url: string): void {
    const match = url.match(/\/workspaces\/([0-9a-f-]{36})/i);
    this.workspaceId.set(match ? match[1] : null);
  }
}
