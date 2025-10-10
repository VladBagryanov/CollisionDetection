import { RcFile } from 'antd/es/upload/interface'

export interface UploadResponse {
  success: boolean
  message: string
  filename?: string
}

export interface CustomUploadProps {
  file: RcFile
  onSuccess?: (response: any) => void
  onError?: (error: Error) => void
  onProgress?: (event: { percent: number }) => void
}

export interface FileUploaderProps {
  onUploadSuccess?: () => void
  onUploadError?: (error: Error) => void
} 