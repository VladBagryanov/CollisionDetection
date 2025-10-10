import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { FactCheckResponse, ApiError } from '../api/client'

interface UseCorpusQueryOptions {
  onSuccess?: (data: FactCheckResponse) => void
  onError?: (error: ApiError) => void
}

export function useCorpusQuery(filePath: string, options: UseCorpusQueryOptions = {}) {
  return useMutation({
    mutationFn: (query: string) => apiClient.queryText(query, filePath),
    onSuccess: (data) => {
      console.log('Query successful:', data)
      options.onSuccess?.(data)
    },
    onError: (error: ApiError) => {
      console.error('Query failed:', error)
      options.onError?.(error)
      
      // Если произошла ошибка, возможно, граф поврежден
      // Сбрасываем состояние, чтобы пересоздать при следующем запросе
      apiClient.resetGraphState()
    }
  })
} 