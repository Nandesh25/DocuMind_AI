export type DocumentStatus = 'uploaded' | 'processing' | 'indexed' | 'failed';

export interface Tag {
  id: string;
  workspace_id: string;
  name: string;
  color: string | null;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  uploaded_by: string | null;
  title: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  status: DocumentStatus;
  error_message: string | null;
  page_count: number | null;
  chunk_count: number | null;
  word_count: number | null;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export type SummaryType = 'short' | 'detailed' | 'executive';

export interface ComparedDocument {
  id: string;
  title: string;
}

export interface ComparisonResult {
  document_a: ComparedDocument;
  document_b: ComparedDocument;
  similarity_score: number;
  comparison: string;
  model_name: string;
}

export type QuizType = 'mcq' | 'true_false' | 'short';

export interface QuizQuestion {
  question: string;
  options: string[] | null;
  answer: string;
  explanation: string | null;
}

export interface QuizResponse {
  document_id: string;
  quiz_type: QuizType;
  model_name: string;
  questions: QuizQuestion[];
}

export interface Flashcard {
  front: string;
  back: string;
  hint: string | null;
}

export interface FlashcardResponse {
  document_id: string;
  model_name: string;
  cards: Flashcard[];
}

export interface Summary {
  id: string;
  document_id: string;
  summary_type: SummaryType;
  content: string;
  model_name: string;
  created_at: string;
}
