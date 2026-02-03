/**
 * OCR API Proxy with Auto-Save to DB
 * 處理 multipart form data，forward 去 backend OCR service，然後自動儲存到 DB
 */

// PostgREST URL (Docker internal network)
const POSTGREST_URL = process.env.POSTGREST_URL || 'http://spellquest_api:3001'

interface VocabularyItem {
  chinese?: string
  english: string
  pinyin?: string
}

interface SaveResult {
  created: any[]
  skipped: { english: string; reason: string }[]
  errors: { english: string; error: string }[]
}

/**
 * 儲存單字到 DB，跳過已存在嘅
 */
async function saveVocabularyToDb(vocabulary: VocabularyItem[]): Promise<SaveResult> {
  const result: SaveResult = {
    created: [],
    skipped: [],
    errors: []
  }
  
  for (const word of vocabulary) {
    if (!word.english || word.english.trim() === '') {
      continue
    }
    
    const english = word.english.trim().toLowerCase()
    
    try {
      // Check if word already exists
      const checkResponse = await fetch(
        `${POSTGREST_URL}/words?english=ilike.${encodeURIComponent(english)}`,
        { method: 'GET', headers: { 'Accept': 'application/json' } }
      )
      
      const existing = await checkResponse.json()
      
      if (existing && existing.length > 0) {
        result.skipped.push({ english, reason: 'already exists' })
        continue
      }
      
      // Insert new word
      const insertResponse = await fetch(`${POSTGREST_URL}/words`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Prefer': 'return=representation'
        },
        body: JSON.stringify({
          english: english,
          chinese: word.chinese?.trim() || '',
          pinyin: '', // Not used anymore
          category: 'ocr', // Mark as OCR-imported
          grade: 'P1'
        })
      })
      
      if (insertResponse.ok) {
        const created = await insertResponse.json()
        result.created.push(created[0] || created)
      } else {
        const errorText = await insertResponse.text()
        result.errors.push({ english, error: errorText })
      }
      
    } catch (error: any) {
      result.errors.push({ english, error: error.message })
    }
  }
  
  return result
}

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
    console.log('OCR Proxy: OCR success, vocabulary count:', data.vocabulary?.length || 0)
    
    // Auto-save to DB
    let saveResult: SaveResult = { created: [], skipped: [], errors: [] }
    if (data.vocabulary && Array.isArray(data.vocabulary) && data.vocabulary.length > 0) {
      console.log('OCR Proxy: saving to DB...')
      saveResult = await saveVocabularyToDb(data.vocabulary)
      console.log('OCR Proxy: DB save complete -', 
        'created:', saveResult.created.length,
        'skipped:', saveResult.skipped.length,
        'errors:', saveResult.errors.length
      )
    }
    
    // Return combined response
    return {
      success: true,
      vocabulary: data.vocabulary || [],
      saved: saveResult
    }
    
  } catch (error: any) {
    console.error('OCR proxy error:', error.message || error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.message || 'OCR service error'
    })
  }
})
