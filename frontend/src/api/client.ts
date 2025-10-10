import axios, { AxiosError, AxiosInstance } from 'axios'
import { setupCache } from 'axios-cache-interceptor'

// Базовые типы из бекенда
export interface FactResult {
  statement: string
  fact: string
  explanation: string
  score?: number
}

export interface FactCheckResponse {
  has_conflicts: boolean
  has_supporting_facts: boolean
  inconsistencies: FactResult[]
  supporting_facts: FactResult[]
  confidence: number
  relevant_facts: string[]
  explanation: string
}

export interface UploadResponse {
  success: boolean
  message: string
  file_path: string // Путь к загруженному файлу
}

export interface ApiError {
  message: string
  code?: string
  details?: unknown
}

// Создаем инстанс axios с базовой конфигурацией
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Добавляем логирование запросов
api.interceptors.request.use(
  (config) => {
    console.log('🚀 Отправка запроса:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
      headers: config.headers
    })
    return config
  },
  (error) => {
    console.error('❌ Ошибка при формировании запроса:', error)
    return Promise.reject(error)
  }
)

// Добавляем логирование ответов
api.interceptors.response.use(
  (response) => {
    console.log('✅ Получен ответ:', {
      status: response.status,
      data: response.data,
      headers: response.headers
    })
    return response
  },
  (error: AxiosError) => {
    console.error('❌ Ошибка ответа:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers,
        data: error.config?.data
      }
    })
    return Promise.reject(error)
  }
)

// Состояние графа для текущей сессии
let hasExistingGraph = false

// Обработчик ошибок
const handleError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string }>
    
    // Проверяем тип ошибки
    if (!axiosError.response) {
      // Нет ответа от сервера
      return {
        message: 'Сервер недоступен. Убедитесь, что бекенд запущен и доступен.',
        code: axiosError.code,
        details: {
          type: 'network_error',
          originalError: axiosError.message
        }
      }
    }

    if (axiosError.code === 'ECONNABORTED') {
      return {
        message: 'Превышено время ожидания ответа от сервера.',
        code: axiosError.code,
        details: {
          type: 'timeout',
          originalError: axiosError.message
        }
      }
    }

    // Ошибка от сервера
    return {
      message: axiosError.response.data?.message || axiosError.message || 'Неизвестная ошибка',
      code: String(axiosError.response.status),
      details: {
        type: 'server_error',
        status: axiosError.response.status,
        data: axiosError.response.data
      }
    }
  }

  // Неизвестная ошибка
  return {
    message: error instanceof Error ? error.message : 'Неизвестная ошибка',
    code: 'unknown',
    details: { originalError: error }
  }
}

// API клиент
export const apiClient = {
  uploadTextFile: async (file: File): Promise<UploadResponse> => {
    // Мокаем успешную загрузку
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          message: 'Файл успешно загружен',
          file_path: 'input_data',
        })
      }, 1000)
    })
  },

  queryText: async (query: string, filePath: string): Promise<FactCheckResponse> => {
    // Мокаем ответ через 4.5 секунды
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          has_conflicts: true,
          has_supporting_facts: false,
          inconsistencies: [
            {
              statement: query,
              fact: 'Arya stark -> Daughter of -> Lord eddard stark',
              explanation: 'The text states that Arya Stark is not the daughter of Eddard Stark, but the fact states that she is the daughter of Lord Eddard Stark.'
            }
          ],
          supporting_facts: [],
          confidence: 0.95,
          relevant_facts: ['Arya stark -> Daughter of -> Lord eddard stark'],
          explanation: 'Противоречие найдено: утверждение не совпадает с известным фактом.'
        })
      }, 4500)
    })
  },

  resetGraphState: () => {}
}

// Мок-данные для тестирования
export const mockResponses = {
  uploadSuccess: {
    success: true,
    message: 'Файл успешно загружен',
    file_path: '/path/to/uploaded/file.txt'
  } as UploadResponse,

  queryResponse: {
    has_conflicts: true,
    has_supporting_facts: true,
    inconsistencies: [
      {
        statement: 'Arya Stark is not the daughter of Eddard Stark',
        fact: 'Arya Stark is the youngest daughter of Eddard Stark',
        explanation: 'The statement directly contradicts the known fact',
        score: 0.95
      }
    ],
    supporting_facts: [
      {
        statement: 'Arya Stark is from Winterfell',
        fact: 'The Stark family resides in Winterfell',
        explanation: 'This fact supports the connection to Winterfell',
        score: 0.85
      }
    ],
    confidence: 0.9,
    relevant_facts: [
      'Arya Stark is the youngest daughter of Eddard Stark',
      'The Stark family resides in Winterfell'
    ],
    explanation: 'The provided statement contradicts established facts about the Stark family.'
  } as FactCheckResponse
} 