declare module '*.module.css' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.css' {
  const css: { [key: string]: string }
  export default css
}

declare module '@ant-design/icons' {
  import { ReactNode } from 'react'
  export const UploadOutlined: ReactNode
  export const SendOutlined: ReactNode
  // Add other icons as needed
} 