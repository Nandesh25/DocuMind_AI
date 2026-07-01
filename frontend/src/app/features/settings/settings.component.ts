import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

import { MATERIAL_IMPORTS } from '@shared/material/material';
import { AuthService } from '@core/services/auth.service';
import { ThemeService } from '@core/services/theme.service';
import { NotificationService } from '@core/services/notification.service';
import { UserApiService } from './services/user-api.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ...MATERIAL_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(UserApiService);
  private readonly notify = inject(NotificationService);
  readonly auth = inject(AuthService);
  readonly theme = inject(ThemeService);

  readonly savingProfile = signal(false);
  readonly savingPassword = signal(false);

  readonly profileForm = this.fb.nonNullable.group({
    full_name: [this.auth.user()?.full_name ?? '', [Validators.required, Validators.minLength(2)]],
  });

  readonly passwordForm = this.fb.nonNullable.group({
    current_password: ['', [Validators.required]],
    new_password: [
      '',
      [
        Validators.required,
        Validators.minLength(8),
        Validators.pattern(/^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/),
      ],
    ],
  });

  saveProfile(): void {
    if (this.profileForm.invalid) {
      return;
    }
    this.savingProfile.set(true);
    this.api.updateProfile(this.profileForm.getRawValue().full_name).subscribe({
      next: () => {
        this.savingProfile.set(false);
        this.auth.loadCurrentUser().subscribe();
        this.notify.success('Profile updated.');
      },
      error: () => this.savingProfile.set(false),
    });
  }

  savePassword(): void {
    if (this.passwordForm.invalid) {
      return;
    }
    this.savingPassword.set(true);
    const { current_password, new_password } = this.passwordForm.getRawValue();
    this.api.changePassword(current_password, new_password).subscribe({
      next: () => {
        this.savingPassword.set(false);
        this.passwordForm.reset();
        this.notify.success('Password changed.');
      },
      error: () => this.savingPassword.set(false),
    });
  }

  setTheme(dark: boolean): void {
    this.theme.set(dark ? 'dark' : 'light');
  }
}
