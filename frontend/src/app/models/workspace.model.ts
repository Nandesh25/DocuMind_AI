export type WorkspaceRole = 'owner' | 'editor' | 'viewer';

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  owner_id: string;
  created_at: string;
}

export interface WorkspaceMember {
  user_id: string;
  email: string;
  full_name: string;
  role: WorkspaceRole;
  joined_at: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string | null;
}
