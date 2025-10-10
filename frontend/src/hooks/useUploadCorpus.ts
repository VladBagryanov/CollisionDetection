import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { UploadResponse } from '../api/client'

interface UseUploadCorpusOptions {
  onSuccess?: (data: UploadResponse) => void
  onError?: (error: Error) => void
  onProgress?: (progress: number) => void
}

export function useUploadCorpus(options: UseUploadCorpusOptions = {}) {
  return useMutation({
    mutationFn: (file: File) => 
      apiClient.uploadDocuments(file, options.onProgress),
    onSuccess: (data) => {
      console.log('Upload successful:', data)
      options.onSuccess?.(data)
    },
    onError: (error: Error) => {
      console.error('Upload failed:', error)
      options.onError?.(error)
    }
  })
} 