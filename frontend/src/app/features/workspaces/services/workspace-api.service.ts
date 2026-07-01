import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@env/environment';
import { PageResponse } from '@interfaces/api-response.interface';
import {
  CreateWorkspaceRequest,
  Workspace,
  WorkspaceMember,
  WorkspaceRole,
} from '@models/workspace.model';

@Injectable({ providedIn: 'root' })
export class WorkspaceApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/workspaces`;

  list(page = 1, size = 20): Observable<PageResponse<Workspace>> {
    const params = new HttpParams().set('page', page).set('size', size);
    return this.http.get<PageResponse<Workspace>>(this.baseUrl, { params });
  }

  get(id: string): Observable<Workspace> {
    return this.http.get<Workspace>(`${this.baseUrl}/${id}`);
  }

  create(payload: CreateWorkspaceRequest): Observable<Workspace> {
    return this.http.post<Workspace>(this.baseUrl, payload);
  }

  update(id: string, payload: Partial<CreateWorkspaceRequest>): Observable<Workspace> {
    return this.http.patch<Workspace>(`${this.baseUrl}/${id}`, payload);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  listMembers(id: string): Observable<WorkspaceMember[]> {
    return this.http.get<WorkspaceMember[]>(`${this.baseUrl}/${id}/members`);
  }

  addMember(
    id: string,
    email: string,
    role: WorkspaceRole,
  ): Observable<WorkspaceMember> {
    return this.http.post<WorkspaceMember>(`${this.baseUrl}/${id}/members`, {
      email,
      role,
    });
  }

  updateMember(
    id: string,
    userId: string,
    role: WorkspaceRole,
  ): Observable<WorkspaceMember> {
    return this.http.patch<WorkspaceMember>(
      `${this.baseUrl}/${id}/members/${userId}`,
      { role },
    );
  }

  removeMember(id: string, userId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}/members/${userId}`);
  }
}
