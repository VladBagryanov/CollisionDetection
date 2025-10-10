import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { FileTextOutlined, ReloadOutlined } from '@ant-design/icons'
import { Card, Alert, List, Button, Space } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../../api/client'
import type { UploadResponse, ApiError } from '../../api/client'
import styles from './FileUploader.module.css'

interface FileUploaderProps {
  onUploadSuccess: (filePath: string) => void
}

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<ApiError | null>(null)

  const uploadMutation = useMutation({
    mutationFn: (file: File) => apiClient.uploadTextFile(file),
    onSuccess: (data) => {
      onUploadSuccess(data.file_path)
      setSelectedFile(null)
      setError(null)
    },
    onError: (error: ApiError) => {
      console.error('Upload error:', error)
      setError(error)
      apiClient.resetGraphState() // Сбрасываем состояние графа при ошибке
    }
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      uploadMutation.mutate(file)
    }
  }, [uploadMutation])

  const handleRetry = useCallback(() => {
    if (selectedFile) {
      setError(null)
      uploadMutation.mutate(selectedFile)
    }
  }, [selectedFile, uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    multiple: false,
    disabled: uploadMutation.isPending
  })

  return (
    <Card className={styles.uploader} title="Загрузка текстового файла">
      <div
        {...getRootProps()}
        className={styles.uploadArea}
        style={{
          borderColor: isDragActive ? '#1677ff' : '#d9d9d9',
          opacity: uploadMutation.isPending ? 0.5 : 1,
        }}
      >
        <input {...getInputProps()} />
        <FileTextOutlined className={styles.icon} />
        <p className={styles.text}>
          {isDragActive
            ? 'Перетащите файл сюда'
            : 'Нажмите или перетащите текстовый файл в эту область'}
        </p>
        <p className={styles.hint}>
          Поддерживается загрузка одного текстового файла в формате .txt
        </p>
      </div>

      {error && (
        <Alert
          message="Ошибка загрузки"
          description={
            <Space direction="vertical">
              <span>{error.message}</span>
              <Button 
                type="primary" 
                icon={<ReloadOutlined />} 
                onClick={handleRetry}
                loading={uploadMutation.isPending}
              >
                Повторить
              </Button>
            </Space>
          }
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          className={styles.error}
        />
      )}

      {selectedFile && (
        <List
          className={styles.fileList}
          size="small"
          bordered
          dataSource={[selectedFile]}
          renderItem={(file) => (
            <List.Item>
              <List.Item.Meta
                title={file.name}
                description={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
              />
              {uploadMutation.isPending && (
                <span>Загрузка...</span>
              )}
            </List.Item>
          )}
        />
      )}
    </Card>
  )
}

export default FileUploader 