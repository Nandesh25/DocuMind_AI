import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

import { NotificationService } from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notify = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // 401s are handled by the refresh interceptor (token refresh / logout).
      if (error.status === 401) {
        return throwError(() => error);
      }
      if (error.status === 503) {
        notify.error('An AI service is temporarily unavailable. Please retry.');
      } else if (error.status >= 500) {
        notify.error('A server error occurred. Please try again later.');
      } else {
        const detail = error.error?.detail;
        if (detail && !req.url.includes('/auth/login')) {
          notify.error(detail);
        }
      }
      return throwError(() => error);
    }),
  );
};
