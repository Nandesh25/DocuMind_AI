import { inject } from '@angular/core';
import {
  HttpErrorResponse,
  HttpInterceptorFn,
  HttpRequest,
} from '@angular/common/http';
import {
  BehaviorSubject,
  catchError,
  filter,
  switchMap,
  take,
  throwError,
} from 'rxjs';

import { AuthService } from '../services/auth.service';
import { TokenService } from '../services/token.service';

// Shared refresh state (interceptor runs in the singleton injector scope).
let isRefreshing = false;
const refreshedToken$ = new BehaviorSubject<string | null>(null);

function isAuthEndpoint(url: string): boolean {
  return (
    url.includes('/auth/login') ||
    url.includes('/auth/register') ||
    url.includes('/auth/refresh') ||
    url.includes('/auth/logout')
  );
}

function withToken(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
}

/**
 * Transparently refreshes an expired access token on a 401 response and
 * retries the failed request. Concurrent 401s are queued until the single
 * in-flight refresh completes.
 */
export const refreshInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const tokens = inject(TokenService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const canRefresh =
        error.status === 401 &&
        !isAuthEndpoint(req.url) &&
        !!tokens.getRefreshToken();

      if (!canRefresh) {
        return throwError(() => error);
      }

      if (isRefreshing) {
        return refreshedToken$.pipe(
          filter((token): token is string => token !== null),
          take(1),
          switchMap((token) => next(withToken(req, token))),
        );
      }

      isRefreshing = true;
      refreshedToken$.next(null);

      return auth.refreshToken().pipe(
        switchMap((res) => {
          isRefreshing = false;
          refreshedToken$.next(res.access_token);
          return next(withToken(req, res.access_token));
        }),
        catchError((refreshError) => {
          isRefreshing = false;
          auth.logout();
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
