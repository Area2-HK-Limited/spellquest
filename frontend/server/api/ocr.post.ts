/**
 * OCR API Proxy (簡化版)
 * 直接 forward request body 去 backend
 */

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  // 用 Docker network 內部連接
  const ocrBackendUrl = process.env.OCR_BACKEND_URL || 'http://spellquest_ocr:3002'
  
  try {
    // 讀取 raw body
    const body = await readRawBody(event)
    const contentType = getHeader(event, 'content-type') || 'multipart/form-data'
    
    console.log('OCR Proxy: forwarding request to', ocrBackendUrl)
    
    // Forward to backend
    const response = await $fetch(`${ocrBackendUrl}/ocr/extract-vocab`, {
      method: 'POST',
      headers: {
        'Content-Type': contentType
      },
      body: body
    })
    
    console.log('OCR Proxy: got response', response)
    return response
    
  } catch (error: any) {
    console.error('OCR proxy error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: error.message || 'OCR service error'
    })
  }
})
