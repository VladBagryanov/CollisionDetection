import React, { Component, ErrorInfo } from 'react'
import { Alert, Button, Typography, Space } from 'antd'
import styles from './ErrorBoundary.module.css'

const { Text, Paragraph } = Typography

interface Props {
  children: React.ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  }

  public static getDerivedStateFromError(error: Error): State {
    console.error('ErrorBoundary caught an error:', error)
    return { hasError: true, error, errorInfo: null }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error)
    console.error('Error info:', errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  private handleReload = () => {
    window.location.reload()
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <Alert
            type="error"
            message="Произошла ошибка в приложении"
            description={
              <Space direction="vertical">
                <Paragraph>
                  К сожалению, произошла непредвиденная ошибка. Попробуйте перезагрузить страницу.
                </Paragraph>
                {process.env.NODE_ENV === 'development' && (
                  <>
                    <Text type="danger">Error: {this.state.error?.message}</Text>
                    <Text type="secondary" className={styles.stackTrace}>
                      {this.state.errorInfo?.componentStack}
                    </Text>
                  </>
                )}
                <Button type="primary" onClick={this.handleReload}>
                  Перезагрузить страницу
                </Button>
              </Space>
            }
          />
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary 