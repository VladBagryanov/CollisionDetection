import React from 'react'
import { Card, Progress, Table, Typography } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import type { QueryResponse, FactResult } from '../../types/api'
import styles from './ResultsDisplay.module.css'

const { Text } = Typography

interface ResultsDisplayProps {
  results: QueryResponse | null
}

const getScoreClass = (score?: number): string => {
  if (!score) return styles.score
  if (score >= 0.8) return `${styles.score} ${styles.scoreHigh}`
  if (score >= 0.5) return `${styles.score} ${styles.scoreMedium}`
  return `${styles.score} ${styles.scoreLow}`
}

const columns: ColumnsType<FactResult> = [
  {
    title: 'Утверждение',
    dataIndex: 'statement',
    key: 'statement',
    render: (text: string, record: FactResult) => (
      <span>
        {text}
        {record.score && (
          <span className={getScoreClass(record.score)}>
            {(record.score * 100).toFixed(0)}%
          </span>
        )}
      </span>
    ),
  },
  {
    title: 'Факт',
    dataIndex: 'fact',
    key: 'fact',
  },
  {
    title: 'Объяснение',
    dataIndex: 'explanation',
    key: 'explanation',
    width: '40%',
  },
]

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  if (!results) return null

  const confidencePercent = Math.round(results.confidence * 100)
  const confidenceStatus = confidencePercent >= 80 ? 'success' : 
                          confidencePercent >= 50 ? 'normal' : 'exception'

  return (
    <Card className={styles.results} title="Результаты проверки">
      <div className={styles.confidence}>
        <div className={styles.confidenceLabel}>
          <span>Уверенность в результатах</span>
          <span className={styles.confidenceValue}>{confidencePercent}%</span>
        </div>
        <Progress percent={confidencePercent} status={confidenceStatus} />
      </div>

      {results.has_supporting_facts && (
        <>
          <h3 className={styles.tableTitle}>Подтверждающие факты</h3>
          <Table
            columns={columns}
            dataSource={results.supporting_facts}
            rowKey={(record) => `support-${record.statement}`}
            pagination={false}
          />
        </>
      )}

      {results.has_conflicts && (
        <>
          <h3 className={styles.tableTitle}>Противоречия</h3>
          <Table
            columns={columns}
            dataSource={results.inconsistencies}
            rowKey={(record) => `conflict-${record.statement}`}
            pagination={false}
          />
        </>
      )}

      <div className={styles.explanation}>
        <h3 className={styles.explanationTitle}>Общее заключение</h3>
        <Text>{results.explanation}</Text>
      </div>
    </Card>
  )
}

export default ResultsDisplay 