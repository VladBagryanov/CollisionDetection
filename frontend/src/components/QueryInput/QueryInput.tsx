import React, { useState } from 'react'
import { Card, Input, Button, Alert, Space } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { useCorpusQuery } from '../../hooks/useCorpusQuery'
import type { FactCheckResponse, ApiError } from '../../api/client'
import styles from './QueryInput.module.css'

const { TextArea } = Input

interface QueryInputProps {
  disabled?: boolean
  filePath: string | null
  onQuerySuccess: (response: FactCheckResponse) => void
}

const QueryInput: React.FC<QueryInputProps> = ({ 
  disabled, 
  filePath,
  onQuerySuccess 
}) => {
  const [query, setQuery] = useState('')
  const [error, setError] = useState<ApiError | null>(null)

  const queryMutation = useCorpusQuery(filePath || '', {
    onSuccess: (data) => {
      onQuerySuccess(data)
      setQuery('')
      setError(null)
    },
    onError: (error) => {
      setError(error)
    }
  })

  const handleSubmit = () => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      setError({
        message: 'Пожалуйста, введите текст запроса'
      })
      return
    }
    if (!filePath) {
      setError({
        message: 'Сначала загрузите текстовый файл'
      })
      return
    }
    setError(null)
    queryMutation.mutate(trimmedQuery)
  }

  if (disabled) {
    return (
      <Card className={styles.queryInput}>
        <Alert
          message="Загрузите текстовый файл"
          description="Для проверки фактов необходимо сначала загрузить текстовый файл"
          type="info"
          showIcon
        />
      </Card>
    )
  }

  return (
    <Card className={styles.queryInput} title="Проверка фактов">
      <TextArea
        className={styles.textarea}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Введите утверждение для проверки..."
        autoSize={{ minRows: 3, maxRows: 6 }}
        disabled={queryMutation.isPending}
      />

      {error && (
        <Alert
          className={styles.error}
          message={error.message}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
        />
      )}

      <Space className={styles.controls}>
        <Button
          type="primary"
          icon={<SendOutlined />}
          loading={queryMutation.isPending}
          onClick={handleSubmit}
          disabled={!query.trim()}
        >
          Проверить факты
        </Button>
        {queryMutation.isPending && (
          <span className={styles.status}>
            Проверяем факты...
          </span>
        )}
      </Space>
    </Card>
  )
}

export default QueryInput 