import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadOutlined } from '@ant-design/icons'
import { Card, Upload, message, Progress } from 'antd'
import type { UploadProps } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { ragApi } from '../api/ragApi'
import type { FileUploaderProps, CustomUploadProps, UploadResponse } from '../types/upload'

const { Dragger } = Upload

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess, onUploadError }) => {
  const uploadMutation = useMutation<UploadResponse, Error, File>({
    mutationFn: ragApi.uploadDocuments,
    onSuccess: (data) => {
      message.success(data.message || 'Файл успешно загружен')
      onUploadSuccess?.()
    },
    onError: (error) => {
      message.error(`Ошибка загрузки: ${error.message}`)
      onUploadError?.(error)
    }
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles[0])
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
    },
    maxFiles: 1,
    multiple: false
  })

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.zip',
    showUploadList: true,
    customRequest: ({ file, onSuccess, onError, onProgress }: CustomUploadProps) => {
      uploadMutation.mutate(file as File, {
        onSuccess: () => onSuccess?.('ok'),
        onError: (error) => onError?.(error),
      })
    }
  }

  return (
    <Card 
      title="Загрузка документов" 
      style={{ maxWidth: 800, margin: '0 auto' }}
      extra={uploadMutation.isLoading && <Progress type="circle" percent={99} size={20} />}
    >
      <Dragger {...uploadProps} disabled={uploadMutation.isLoading}>
        <p className="ant-upload-drag-icon">
          <UploadOutlined style={{ fontSize: 48, color: '#1677ff' }} />
        </p>
        <p className="ant-upload-text">
          Нажмите или перетащите ZIP-файл в эту область
        </p>
        <p className="ant-upload-hint">
          Поддерживается загрузка одного ZIP-архива с текстовыми документами
        </p>
      </Dragger>
    </Card>
  )
}

export default FileUploader 