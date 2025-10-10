import { QueryClient } from '@tanstack/react-query'

const isDevelopment = process.env.NODE_ENV === 'development'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: isDevelopment ? false : 3,
      staleTime: 5 * 60 * 1000, // 5 минут
      cacheTime: 10 * 60 * 1000, // 10 минут
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: false,
      onError: (error) => {
        console.error('Mutation error:', error)
      }
    }
  },
}) 