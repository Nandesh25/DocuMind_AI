import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LoadingService {
  private activeRequests = 0;
  private readonly loadingState = signal(false);
  readonly isLoading = this.loadingState.asReadonly();

  start(): void {
    this.activeRequests++;
    this.loadingState.set(true);
  }

  stop(): void {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    if (this.activeRequests === 0) {
      this.loadingState.set(false);
    }
  }
}
