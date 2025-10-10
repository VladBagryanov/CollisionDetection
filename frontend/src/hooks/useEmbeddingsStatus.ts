import { useQuery } from '@tanstack/react-query'
import { apiClient, EmbeddingsStatus } from '../api/client'

const POLLING_INTERVAL = 2000 // 2 seconds
export const EMBEDDINGS_STATUS_KEY = ['embeddings', 'status']

export function useEmbeddingsStatus() {
  return useQuery<EmbeddingsStatus, Error>({
    queryKey: EMBEDDINGS_STATUS_KEY,
    queryFn: apiClient.getEmbeddingsStatus,
    refetchInterval: (data) => {
      if (data?.status === 'ready' || data?.status === 'error') {
        return false
      }
      return POLLING_INTERVAL
    },
    retry: false,
    refetchOnWindowFocus: true,
  })
}

export function useIsEmbeddingsReady() {
  const { data } = useEmbeddingsStatus()
  return data?.status === 'ready'
} 