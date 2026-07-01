import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { User } from '@models/user.model';

@Injectable({ providedIn: 'root' })
export class UserApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/users`;

  updateProfile(fullName: string): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/me`, { full_name: fullName });
  }

  changePassword(
    currentPassword: string,
    newPassword: string,
  ): Observable<void> {
    return this.http.put<void>(`${this.baseUrl}/me/password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }
}
