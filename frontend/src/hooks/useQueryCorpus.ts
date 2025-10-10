import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient, FactCheckResponse } from '../api/client'
import { EMBEDDINGS_STATUS_KEY } from './useEmbeddingsStatus'

interface UseQueryCorpusOptions {
  onSuccess?: (data: FactCheckResponse) => void
  onError?: (error: Error) => void
}

export function useQueryCorpus(options: UseQueryCorpusOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (text: string) => apiClient.queryCorpus(text),
    onSuccess: (data) => {
      console.log('Query successful:', data)
      options.onSuccess?.(data)
      
      // Обновляем статус эмбеддингов после успешного запроса
      queryClient.invalidateQueries({ queryKey: EMBEDDINGS_STATUS_KEY })
    },
    onError: (error: Error) => {
      console.error('Query failed:', error)
      options.onError?.(error)
    }
  })
} 