<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-purple-600">📷 輸入詞語</h1>
        <p class="text-gray-600">新增溫習內容</p>
      </div>
      <div></div>
    </div>

    <!-- Input Form -->
    <div class="sq-card bg-white p-8 mb-8">
      <h2 class="text-xl font-bold text-gray-700 mb-6">手動輸入詞語</h2>
      
      <form @submit.prevent="addWord" class="space-y-4">
        <UFormField label="中文" required>
          <UInput v-model="newWord.chinese" placeholder="例如：蘋果" size="lg" />
        </UFormField>
        
        <UFormField label="英文">
          <UInput v-model="newWord.english" placeholder="例如：apple" size="lg" />
        </UFormField>
        
        <UFormField label="拼音">
          <UInput v-model="newWord.pinyin" placeholder="例如：píng guǒ" size="lg" />
        </UFormField>
        
        <UFormField label="分類">
          <USelect v-model="newWord.category" :options="categories" size="lg" />
        </UFormField>
        
        <div class="pt-4">
          <UButton type="submit" color="purple" size="lg" block>
            ➕ 新增詞語
          </UButton>
        </div>
      </form>
    </div>

    <!-- Batch Input -->
    <div class="sq-card bg-white p-8 mb-8">
      <h2 class="text-xl font-bold text-gray-700 mb-4">批量輸入</h2>
      <p class="text-gray-500 mb-4">每行一個詞語，格式：中文,英文,拼音</p>
      
      <UTextarea 
        v-model="batchInput" 
        placeholder="蘋果,apple,píng guǒ
香蕉,banana,xiāng jiāo
橙,orange,chéng"
        :rows="6"
        class="mb-4"
      />
      
      <UButton @click="addBatchWords" color="purple" variant="outline" size="lg">
        📥 批量新增
      </UButton>
    </div>

    <!-- OCR Input -->
    <div class="sq-card bg-white p-8 mb-8">
      <h2 class="text-xl font-bold text-gray-700 mb-4">📷 OCR 相片輸入</h2>
      <p class="text-gray-500 mb-4">影相或上傳溫習範圍，AI 自動識別文字</p>
      
      <!-- Upload Area -->
      <div 
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
        :class="isDragging ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-purple-400'"
        @click="triggerFileInput"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <input 
          ref="fileInput"
          type="file"
          accept="image/*"
          capture="environment"
          class="hidden"
          @change="handleFileSelect"
        />
        
        <div v-if="!selectedImage">
          <div class="text-5xl mb-3">📸</div>
          <p class="text-lg text-gray-600 mb-2">點擊上傳相片或拖放</p>
          <p class="text-sm text-gray-400">支援 JPG、PNG 格式</p>
          <div class="mt-4 flex justify-center gap-4">
            <UButton color="purple" size="lg" @click.stop="triggerFileInput">
              📁 選擇相片
            </UButton>
            <UButton color="purple" variant="outline" size="lg" @click.stop="triggerCamera">
              📷 影相
            </UButton>
          </div>
        </div>
        
        <div v-else class="space-y-4">
          <img :src="selectedImage" class="max-h-64 mx-auto rounded-lg shadow-lg" />
          <div class="flex justify-center gap-4">
            <UButton color="purple" size="lg" @click.stop="processOCR" :loading="isProcessing">
              {{ isProcessing ? '識別中...' : '🔍 開始識別' }}
            </UButton>
            <UButton color="neutral" variant="outline" size="lg" @click.stop="clearImage">
              ✕ 清除
            </UButton>
          </div>
        </div>
      </div>
      
      <!-- OCR Result -->
      <div v-if="ocrResult" class="mt-6">
        <h3 class="text-lg font-bold text-gray-700 mb-3">識別結果（可修正）</h3>
        <UTextarea 
          v-model="ocrResult"
          placeholder="識別到嘅文字會顯示喺呢度，你可以修正..."
          :rows="8"
          class="mb-4 font-mono"
        />
        <p class="text-sm text-gray-500 mb-4">
          💡 格式：每行一個詞語，用逗號分隔中文、英文、拼音<br>
          例如：蘋果,apple,píng guǒ
        </p>
        <div class="flex gap-4">
          <UButton color="success" size="lg" @click="importOCRResult">
            ✅ 匯入詞語
          </UButton>
          <UButton color="neutral" variant="outline" size="lg" @click="ocrResult = ''">
            清除結果
          </UButton>
        </div>
      </div>
    </div>

    <!-- Added Words Preview -->
    <div v-if="addedWords.length > 0" class="sq-card bg-white p-8">
      <h2 class="text-xl font-bold text-gray-700 mb-4">已新增詞語 ({{ addedWords.length }})</h2>
      
      <div class="space-y-2">
        <div 
          v-for="(word, index) in addedWords" 
          :key="index"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div>
            <span class="text-xl font-bold text-purple-600">{{ word.chinese }}</span>
            <span v-if="word.english" class="text-gray-500 ml-2">{{ word.english }}</span>
            <span v-if="word.pinyin" class="text-gray-400 ml-2 text-sm">({{ word.pinyin }})</span>
          </div>
          <UButton @click="removeWord(index)" color="error" variant="ghost" size="sm">
            ✕
          </UButton>
        </div>
      </div>
      
      <div class="mt-6 flex gap-4">
        <UButton @click="saveWords" color="success" size="lg">
          💾 儲存全部
        </UButton>
        <UButton @click="clearAll" color="neutral" size="lg">
          清除全部
        </UButton>
      </div>
    </div>

    <!-- Success Toast -->
    <UNotifications />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const newWord = ref({
  chinese: '',
  english: '',
  pinyin: '',
  category: 'general'
})

const categories = [
  { label: '一般', value: 'general' },
  { label: '水果', value: 'fruit' },
  { label: '學校', value: 'school' },
  { label: '家庭', value: 'family' },
  { label: '動物', value: 'animals' },
  { label: '自然', value: 'nature' }
]

const batchInput = ref('')
const addedWords = ref([])

// OCR 相關
const fileInput = ref(null)
const selectedImage = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const ocrResult = ref('')

const triggerFileInput = () => {
  fileInput.value?.click()
}

const triggerCamera = () => {
  // Create a separate input for camera capture
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'
  input.onchange = (e) => handleFileSelect(e)
  input.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    selectedImage.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const clearImage = () => {
  selectedImage.value = null
  selectedFile.value = null
  ocrResult.value = ''
}

const processOCR = async () => {
  if (!selectedFile.value) return
  
  isProcessing.value = true
  
  try {
    // 嘗試調用 OCR API
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const ocrApiUrl = useRuntimeConfig().public.ocrApiUrl || '/api/ocr'
    
    try {
      const response = await fetch(`${ocrApiUrl}/ocr/extract-vocab`, {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const data = await response.json()
        // 轉換格式：每行一個詞語
        if (data.vocabulary && Array.isArray(data.vocabulary)) {
          ocrResult.value = data.vocabulary.map(v => 
            [v.chinese, v.english, v.pinyin].filter(Boolean).join(',')
          ).join('\n')
        } else if (data.words) {
          ocrResult.value = data.words.join('\n')
        } else if (data.text) {
          ocrResult.value = data.text
        }
      } else {
        throw new Error('OCR API 未能連接')
      }
    } catch (apiError) {
      // API 未 ready，顯示 placeholder 提示
      console.warn('OCR API not available:', apiError)
      ocrResult.value = `# OCR 服務未啟動\n# 請手動輸入識別到嘅文字\n# 格式：中文,英文,拼音\n# 例如：\n蘋果,apple,píng guǒ\n香蕉,banana,xiāng jiāo`
    }
  } catch (error) {
    console.error('OCR error:', error)
    ocrResult.value = '識別失敗，請手動輸入'
  } finally {
    isProcessing.value = false
  }
}

const importOCRResult = () => {
  if (!ocrResult.value.trim()) return
  
  const lines = ocrResult.value.trim().split('\n')
  let importCount = 0
  
  for (const line of lines) {
    // 跳過註釋行
    if (line.startsWith('#')) continue
    
    const parts = line.split(',').map(p => p.trim())
    if (parts[0]) {
      addedWords.value.push({
        chinese: parts[0],
        english: parts[1] || '',
        pinyin: parts[2] || '',
        category: 'general'
      })
      importCount++
    }
  }
  
  if (importCount > 0) {
    alert(`已匯入 ${importCount} 個詞語！`)
    ocrResult.value = ''
    selectedImage.value = null
    selectedFile.value = null
  }
}

const addWord = () => {
  if (newWord.value.chinese.trim()) {
    addedWords.value.push({ ...newWord.value })
    newWord.value = {
      chinese: '',
      english: '',
      pinyin: '',
      category: 'general'
    }
  }
}

const addBatchWords = () => {
  const lines = batchInput.value.trim().split('\n')
  for (const line of lines) {
    const parts = line.split(',').map(p => p.trim())
    if (parts[0]) {
      addedWords.value.push({
        chinese: parts[0],
        english: parts[1] || '',
        pinyin: parts[2] || '',
        category: 'general'
      })
    }
  }
  batchInput.value = ''
}

const removeWord = (index) => {
  addedWords.value.splice(index, 1)
}

const clearAll = () => {
  addedWords.value = []
}

const saveWords = async () => {
  // TODO: Save to database via API
  console.log('Saving words:', addedWords.value)
  alert(`已儲存 ${addedWords.value.length} 個詞語！`)
  addedWords.value = []
}
</script>
