import React, { useState } from 'react'
import { ConfigProvider, Layout, theme, Spin, Typography, Button } from 'antd'
import FileUploader from './components/FileUploader/FileUploader'
import QueryInput from './components/QueryInput/QueryInput'
import ResultsDisplay from './components/ResultsDisplay/ResultsDisplay'
import type { FactCheckResponse } from './api/client'

const { Content } = Layout
const { Title } = Typography

function App() {
  const [currentFilePath, setCurrentFilePath] = useState<string | null>(null)
  const [queryResults, setQueryResults] = useState<FactCheckResponse | null>(null)
  const [isBuilding, setIsBuilding] = useState(false)
  const [isBuilt, setIsBuilt] = useState(false)

  // Для имитации долгой сборки графа
  const handleUploadSuccess = (filePath: string) => {
    setCurrentFilePath(filePath)
    setQueryResults(null)
    setIsBuilding(true)
    setIsBuilt(false)
    setTimeout(() => {
      setIsBuilding(false)
      setIsBuilt(true)
    }, 53000) // 53 секунды
  }

  // После успешного запроса сбрасываем результаты
  const handleQuerySuccess = (result: FactCheckResponse) => {
    setQueryResults(result)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '24px', background: '#f5f5f5', maxWidth: 700, margin: '0 auto' }}>
        <Title level={2} style={{ textAlign: 'center', margin: '32px 0' }}>Графовый RAG агент для поиска противоречий в тексте</Title>
        {!currentFilePath && (
          <FileUploader onUploadSuccess={handleUploadSuccess} />
        )}
        {isBuilding && (
          <div style={{ textAlign: 'center', marginTop: 48 }}>
            <Spin size="large" tip="Построение графа..." style={{ marginBottom: 16 }} />
            <div style={{ marginTop: 16 }}>Идет построение графа на вашем файле. Пожалуйста, подождите ~1 минуту...</div>
          </div>
        )}
        {isBuilt && (
          <div style={{ textAlign: 'center', margin: '32px 0' }}>
            <Title level={4} type="success">Графовый RAG на данном файле успешно построен.</Title>
            <QueryInput
              disabled={false}
              filePath={currentFilePath}
              onQuerySuccess={handleQuerySuccess}
            />
            <ResultsDisplay results={queryResults} />
          </div>
        )}
      </Content>
    </Layout>
  )
}

export default App 