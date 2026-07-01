import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { PageResponse } from '@interfaces/api-response.interface';
import {
  ComparisonResult,
  DocumentItem,
  DocumentStatus,
  FlashcardResponse,
  QuizResponse,
  QuizType,
  Summary,
  Tag,
} from '@models/document.model';

@Injectable({ providedIn: 'root' })
export class DocumentApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  list(
    workspaceId: string,
    page = 1,
    size = 20,
    status?: DocumentStatus,
    q?: string,
  ): Observable<PageResponse<DocumentItem>> {
    let params = new HttpParams().set('page', page).set('size', size);
    if (status) {
      params = params.set('status', status);
    }
    if (q) {
      params = params.set('q', q);
    }
    return this.http.get<PageResponse<DocumentItem>>(
      `${this.baseUrl}/workspaces/${workspaceId}/documents`,
      { params },
    );
  }

  get(documentId: string): Observable<DocumentItem> {
    return this.http.get<DocumentItem>(`${this.baseUrl}/documents/${documentId}`);
  }

  upload(
    workspaceId: string,
    file: File,
    title?: string,
  ): Observable<DocumentItem> {
    const form = new FormData();
    form.append('file', file);
    if (title) {
      form.append('title', title);
    }
    return this.http.post<DocumentItem>(
      `${this.baseUrl}/workspaces/${workspaceId}/documents`,
      form,
    );
  }

  delete(documentId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/documents/${documentId}`);
  }

  reindex(documentId: string): Observable<DocumentItem> {
    return this.http.post<DocumentItem>(
      `${this.baseUrl}/documents/${documentId}/reindex`,
      {},
    );
  }

  downloadUrl(documentId: string): string {
    return `${this.baseUrl}/documents/${documentId}/download`;
  }

  // --- Summaries ---
  listSummaries(documentId: string): Observable<Summary[]> {
    return this.http.get<Summary[]>(
      `${this.baseUrl}/documents/${documentId}/summaries`,
    );
  }

  generateSummary(
    documentId: string,
    summaryType: Summary['summary_type'],
  ): Observable<Summary> {
    return this.http.post<Summary>(
      `${this.baseUrl}/documents/${documentId}/summaries`,
      { summary_type: summaryType },
    );
  }

  // --- Tags ---
  listTags(workspaceId: string): Observable<Tag[]> {
    return this.http.get<Tag[]>(
      `${this.baseUrl}/workspaces/${workspaceId}/tags`,
    );
  }

  // --- Comparison ---
  compare(
    workspaceId: string,
    documentAId: string,
    documentBId: string,
  ): Observable<ComparisonResult> {
    return this.http.post<ComparisonResult>(
      `${this.baseUrl}/workspaces/${workspaceId}/compare`,
      { document_a_id: documentAId, document_b_id: documentBId },
    );
  }

  // --- Quiz ---
  generateQuiz(
    documentId: string,
    quizType: QuizType,
    numQuestions: number,
  ): Observable<QuizResponse> {
    return this.http.post<QuizResponse>(
      `${this.baseUrl}/documents/${documentId}/quiz`,
      { quiz_type: quizType, num_questions: numQuestions },
    );
  }

  // --- Flashcards ---
  generateFlashcards(
    documentId: string,
    numCards: number,
  ): Observable<FlashcardResponse> {
    return this.http.post<FlashcardResponse>(
      `${this.baseUrl}/documents/${documentId}/flashcards`,
      { num_cards: numCards },
    );
  }
}
