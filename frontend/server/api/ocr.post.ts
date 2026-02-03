/**
 * OCR API Proxy
 * 處理 multipart form data 並 forward 去 backend OCR service
 */

export default defineEventHandler(async (event) => {
  // 用 Docker network 內部連接
  const ocrBackendUrl = process.env.OCR_BACKEND_URL || 'http://spellquest_ocr:3002'
  
  try {
    // 讀取 multipart form data
    const formDataItems = await readMultipartFormData(event)
    
    if (!formDataItems || formDataItems.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded'
      })
    }
    
    // 搵 file field
    const fileField = formDataItems.find(f => f.name === 'file')
    if (!fileField) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file field found'
      })
    }
    
    console.log('OCR Proxy: file received', fileField.filename, fileField.type, fileField.data?.length, 'bytes')
    
    // 用 Node 20 native FormData
    const backendForm = new FormData()
    const blob = new Blob([fileField.data], { type: fileField.type || 'image/jpeg' })
    backendForm.append('file', blob, fileField.filename || 'image.jpg')
    
    console.log('OCR Proxy: forwarding to', `${ocrBackendUrl}/ocr/extract-vocab`)
    
    // Forward to backend using native fetch
    const response = await fetch(`${ocrBackendUrl}/ocr/extract-vocab`, {
      method: 'POST',
      body: backendForm
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('OCR API error:', response.status, errorText)
      throw createError({
        statusCode: response.status,
        statusMessage: `OCR API error: ${errorText}`
      })
    }
    
    const data = await response.json()
    console.log('OCR Proxy: success', JSON.stringify(data).slice(0, 200))
    return data
    
  } catch (error: any) {
    console.error('OCR proxy error:', error.message || error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'OCR service error'
    })
  }
})
