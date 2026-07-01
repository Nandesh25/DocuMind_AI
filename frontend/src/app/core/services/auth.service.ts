import { computed, inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '@env/environment';
import { LoginRequest, RegisterRequest, TokenResponse } from '@interfaces/auth.interface';
import { User } from '@models/user.model';
import { TokenService } from './token.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokens = inject(TokenService);
  private readonly router = inject(Router);
  private readonly baseUrl = `${environment.apiUrl}/auth`;

  private readonly currentUser = signal<User | null>(null);
  readonly user = this.currentUser.asReadonly();
  readonly isAuthenticated = computed(() => this.currentUser() !== null);

  login(payload: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.baseUrl}/login`, payload).pipe(
      tap((res) => this.tokens.setTokens(res.access_token, res.refresh_token)),
    );
  }

  register(payload: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/register`, payload);
  }

  loadCurrentUser(): Observable<User> {
    return this.http
      .get<User>(`${environment.apiUrl}/users/me`)
      .pipe(tap((user) => this.currentUser.set(user)));
  }

  refreshToken(): Observable<TokenResponse> {
    const refresh_token = this.tokens.getRefreshToken();
    return this.http
      .post<TokenResponse>(`${this.baseUrl}/refresh`, { refresh_token })
      .pipe(tap((res) => this.tokens.setTokens(res.access_token, res.refresh_token)));
  }

  logout(): void {
    const refreshToken = this.tokens.getRefreshToken();
    if (refreshToken) {
      // Best-effort server-side revocation; clear the session regardless.
      this.http
        .post(`${this.baseUrl}/logout`, { refresh_token: refreshToken })
        .subscribe({
          next: () => this.finalizeLogout(),
          error: () => this.finalizeLogout(),
        });
    } else {
      this.finalizeLogout();
    }
  }

  private finalizeLogout(): void {
    this.tokens.clear();
    this.currentUser.set(null);
    void this.router.navigate(['/auth/login']);
  }

  hasSession(): boolean {
    return this.tokens.hasToken();
  }
}
