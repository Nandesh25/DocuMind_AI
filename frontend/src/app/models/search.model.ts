export interface SearchRequest {
  query: string;
  top_k?: number;
  document_ids?: string[];
  min_score?: number;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  content: string;
  score: number;
  page_number: number | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}
