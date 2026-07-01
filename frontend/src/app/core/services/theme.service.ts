import { Injectable, signal } from '@angular/core';

type ThemeMode = 'light' | 'dark';
const THEME_KEY = 'documind_theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly mode = signal<ThemeMode>(this.readInitial());
  readonly theme = this.mode.asReadonly();

  constructor() {
    this.apply(this.mode());
  }

  toggle(): void {
    this.set(this.mode() === 'light' ? 'dark' : 'light');
  }

  set(mode: ThemeMode): void {
    this.mode.set(mode);
    localStorage.setItem(THEME_KEY, mode);
    this.apply(mode);
  }

  private apply(mode: ThemeMode): void {
    document.documentElement.style.colorScheme = mode;
  }

  private readInitial(): ThemeMode {
    const stored = localStorage.getItem(THEME_KEY) as ThemeMode | null;
    if (stored) {
      return stored;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
}
