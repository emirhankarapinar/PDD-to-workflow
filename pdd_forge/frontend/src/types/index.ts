export interface PDDSection {
  id: string;
  name: string;
  content: string;
  pages: string;
  confidence: number;
}

export interface Statistics {
  total_pages: number;
  pages_with_tables: number;
  pages_with_images: number;
  total_words: number;
  avg_words_per_page: number;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  statistics: Statistics;
  sections: PDDSection[];
  message: string;
}

export interface GenerateResponse {
  session_id: string;
  project_name: string;
  project_path: string;
  quality_score: number;
  steps_count: number;
  warnings: string[];
  message: string;
}

export interface SessionInfo {
  session_id: string;
  filename: string;
  statistics: Statistics;
  sections_count: number;
  project_generated: boolean;
  quality_score?: number;
  project_name?: string;
}
