import axios, { AxiosError } from 'axios'
import type { 
  ApiResponse, 
  UploadResponse, 
  QueryRequest, 
  QueryResponse,
  EmbeddingsStatus 
} from '../types/api'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message: string }>) => {
    const message = error.response?.data?.message || error.message || 'Неизвестная ошибка'
    return Promise.reject(new Error(message))
  }
)

export const ragApi = {
  uploadDocuments: async (file: File, onProgress?: (percent: number) => void): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<ApiResponse<UploadResponse>>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress?.(percentCompleted)
        }
      }
    })
    return response.data.data
  },

  getEmbeddingsStatus: async (): Promise<EmbeddingsStatus> => {
    const response = await api.get<ApiResponse<EmbeddingsStatus>>('/embeddings-status')
    return response.data.data
  },

  query: async (data: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post<ApiResponse<QueryResponse>>('/query', data)
    return response.data.data
  },
}

export default ragApi 