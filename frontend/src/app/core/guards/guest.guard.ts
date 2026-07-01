import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from '../services/auth.service';

/**
 * Prevents authenticated users from visiting auth pages (login/register).
 */
export const guestGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.hasSession()) {
    return true;
  }
  return router.createUrlTree(['/workspaces']);
};
