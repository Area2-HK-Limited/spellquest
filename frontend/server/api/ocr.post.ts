/**
 * OCR API Proxy
 * 將 client 嘅 OCR request proxy 去 backend OCR service
 * 避免 CORS 問題（手機 browser 不能直接 access 內網 IP）
 */

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const ocrApiUrl = config.public.ocrApiUrl || 'http://localhost:3002'
  
  try {
    // 讀取 multipart form data
    const formData = await readMultipartFormData(event)
    
    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded'
      })
    }
    
    // 搵 file field
    const fileField = formData.find(f => f.name === 'file')
    if (!fileField) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file field found'
      })
    }
    
    // 建立新嘅 FormData 俾 backend
    const backendFormData = new FormData()
    const blob = new Blob([fileField.data], { type: fileField.type || 'image/jpeg' })
    backendFormData.append('file', blob, fileField.filename || 'image.jpg')
    
    // Call backend OCR API
    const response = await fetch(`${ocrApiUrl}/ocr/extract-vocab`, {
      method: 'POST',
      body: backendFormData
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('OCR API error:', errorText)
      throw createError({
        statusCode: response.status,
        statusMessage: `OCR API error: ${errorText}`
      })
    }
    
    const data = await response.json()
    return data
    
  } catch (error: any) {
    console.error('OCR proxy error:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'OCR service error'
    })
  }
})
