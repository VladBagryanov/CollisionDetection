export interface ApiError {
  message: string
  code?: string
  details?: unknown
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  error?: ApiError
}

export interface UploadResponse {
  success: boolean
  message: string
  filename?: string
}

export interface EmbeddingsStatus {
  status: 'pending' | 'processing' | 'ready' | 'error'
  progress: number
  total_files?: number
  processed_files?: number
  error_message?: string
}

export interface QueryRequest {
  text: string
  facts?: string[]
}

export interface FactResult {
  statement: string
  fact: string
  explanation: string
  score?: number
}

export interface QueryResponse {
  has_conflicts: boolean
  has_supporting_facts: boolean
  inconsistencies: FactResult[]
  supporting_facts: FactResult[]
  confidence: number
  relevant_facts: string[]
  explanation: string
} 