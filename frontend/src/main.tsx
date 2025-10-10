import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App'
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary'
import { queryClient } from './lib/queryClient'
import './index.css'

// Глобальный обработчик необработанных ошибок
window.onerror = (message, source, lineno, colno, error) => {
  console.error('Global error:', { message, source, lineno, colno, error })
}

// Глобальный обработчик необработанных промисов
window.onunhandledrejection = (event) => {
  console.error('Unhandled promise rejection:', event.reason)
}

// Логирование монтирования приложения
console.log('Starting application...')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
        {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
) 