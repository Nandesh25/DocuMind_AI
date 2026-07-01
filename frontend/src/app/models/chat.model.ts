export type MessageRole = 'user' | 'assistant' | 'system';

export interface Chat {
  id: string;
  workspace_id: string;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface MessageSource {
  document_id: string;
  chunk_id: string;
  relevance_score: number | null;
  rank: number | null;
}

export interface ChatMessage {
  id: string;
  chat_id: string;
  role: MessageRole;
  content: string;
  model_name: string | null;
  latency_ms: number | null;
  sources: MessageSource[];
  created_at: string;
}

export interface SendMessageRequest {
  content: string;
  top_k?: number;
  document_ids?: string[];
}
