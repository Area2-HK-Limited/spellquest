<template>
  <UContainer>
    <div class="py-8">
      <!-- Header -->
      <UPageHeader
        title="📷 輸入詞語"
        description="新增溫習內容"
      >
        <template #links>
          <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left">返回</UButton>
        </template>
      </UPageHeader>

      <!-- Success Alert -->
      <UAlert
        v-if="successMessage"
        color="green"
        variant="subtle"
        :title="successMessage"
        icon="i-heroicons-check-circle"
        class="mb-6"
        @close="successMessage = ''"
      />

      <!-- Error Alert -->
      <UAlert
        v-if="errorMessage"
        color="red"
        variant="subtle"
        :title="errorMessage"
        icon="i-heroicons-exclamation-circle"
        class="mb-6"
        @close="errorMessage = ''"
      />

      <!-- Manual Input Form -->
      <UCard class="mb-8">
        <template #header>
          <h2 class="text-xl font-bold">手動輸入詞語</h2>
        </template>
        
        <UForm :state="newWord" @submit="addWord" class="space-y-4">
          <UFormGroup label="英文" name="english" required>
            <UInput v-model="newWord.english" placeholder="例如：apple" size="lg" />
          </UFormGroup>
          
          <UFormGroup label="中文" name="chinese">
            <UInput v-model="newWord.chinese" placeholder="例如：蘋果" size="lg" />
          </UFormGroup>
          
          <UFormGroup label="分類" name="category">
            <USelect v-model="newWord.category" :options="categories" size="lg" />
          </UFormGroup>
          
          <UButton type="submit" color="primary" size="lg" block icon="i-heroicons-plus">
            新增詞語
          </UButton>
        </UForm>
      </UCard>

      <!-- Batch Input -->
      <UCard class="mb-8">
        <template #header>
          <h2 class="text-xl font-bold">批量輸入</h2>
          <p class="text-sm text-gray-600 mt-1">每行一個詞語，格式：英文,中文</p>
        </template>
        
        <UTextarea 
          v-model="batchInput" 
          placeholder="apple,蘋果
banana,香蕉
orange,橙"
          :rows="6"
          class="mb-4"
        />
        
        <UButton @click="addBatchWords" color="primary" variant="outline" size="lg" icon="i-heroicons-arrow-down-tray">
          批量新增
        </UButton>
      </UCard>

      <!-- OCR Input -->
      <UCard class="mb-8">
        <template #header>
          <h2 class="text-xl font-bold">📷 OCR 相片輸入</h2>
          <p class="text-sm text-gray-600 mt-1">影相或上傳溫習範圍，AI 自動識別文字</p>
        </template>
        
        <!-- Upload Area -->
        <div 
          class="border-2 border-dashed rounded-xl p-8 text-center transition-all"
          :class="isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300'"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
        >
          <input 
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleFileSelect"
          />
          
          <input 
            ref="cameraInput"
            type="file"
            accept="image/*"
            capture="environment"
            class="hidden"
            @change="handleFileSelect"
          />
          
          <div v-if="!selectedImage">
            <div class="text-5xl mb-3">📸</div>
            <p class="text-lg text-gray-600 mb-2">選擇相片或拖放到此</p>
            <p class="text-sm text-gray-600 mb-4">支援 JPG、PNG 格式</p>
            <div class="flex justify-center gap-4">
              <UButton color="primary" size="lg" @click="triggerFileInput" icon="i-heroicons-folder">
                選擇相片
              </UButton>
              <UButton color="primary" variant="outline" size="lg" @click="triggerCamera" icon="i-heroicons-camera">
                影相
              </UButton>
            </div>
          </div>
          
          <div v-else class="space-y-4">
            <img :src="selectedImage" class="max-h-64 mx-auto rounded-lg shadow-lg" />
            <div class="flex justify-center gap-4">
              <UButton color="primary" size="lg" @click="processOCR" :loading="isProcessing" icon="i-heroicons-magnifying-glass">
                {{ isProcessing ? '識別中...' : '開始識別' }}
              </UButton>
              <UButton color="gray" variant="outline" size="lg" @click="clearImage" icon="i-heroicons-x-mark">
                清除
              </UButton>
            </div>
          </div>
        </div>
        
        <!-- OCR Progress -->
        <UProgress v-if="isProcessing" :value="ocrProgress" class="mt-4" />
        
        <!-- OCR Result -->
        <div v-if="ocrResult" class="mt-6">
          <h3 class="text-lg font-bold mb-3">識別結果（可修正）</h3>
          <UTextarea 
            v-model="ocrResult"
            placeholder="識別到嘅文字會顯示喺呢度，你可以修正..."
            :rows="8"
            class="mb-4 font-mono"
          />
          <UAlert 
            color="blue" 
            variant="subtle"
            class="mb-4"
          >
            <template #title>
              💡 格式：每行一個詞語，用逗號分隔英文、中文
            </template>
            <template #description>
              例如：apple,蘋果
            </template>
          </UAlert>
          <div class="flex gap-4">
            <UButton color="green" size="lg" @click="importOCRResult" icon="i-heroicons-check">
              匯入詞語
            </UButton>
            <UButton color="gray" variant="outline" size="lg" @click="ocrResult = ''" icon="i-heroicons-trash">
              清除結果
            </UButton>
          </div>
        </div>
      </UCard>

      <!-- Added Words Preview -->
      <UCard v-if="addedWords.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-bold">已新增詞語</h2>
            <UBadge color="primary" size="lg">{{ addedWords.length }}</UBadge>
          </div>
        </template>
        
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div 
            v-for="(word, index) in addedWords" 
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="text-xl font-bold text-primary-600">{{ word.english }}</span>
              <span v-if="word.chinese" class="text-gray-700 ml-2">{{ word.chinese }}</span>
              <UBadge v-if="word.category" color="gray" size="sm" class="ml-2">{{ word.category }}</UBadge>
            </div>
            <UButton @click="removeWord(index)" color="red" variant="ghost" size="sm" icon="i-heroicons-x-mark" />
          </div>
        </div>
        
        <template #footer>
          <div class="flex gap-4">
            <UButton @click="saveWords" color="green" size="lg" :loading="isSaving" icon="i-heroicons-check">
              儲存詞語
            </UButton>
            <UButton @click="clearAll" color="gray" size="lg" icon="i-heroicons-trash">
              清除全部
            </UButton>
          </div>
        </template>
      </UCard>
    </div>
  </UContainer>
</template>

<script setup>
import { ref } from 'vue'

// Success/Error messages
const successMessage = ref('')
const errorMessage = ref('')

const newWord = ref({
  english: '',
  chinese: '',
  category: 'custom'
})

const categories = [
  { label: '自訂', value: 'custom' },
  { label: '水果', value: 'fruit' },
  { label: '學校', value: 'school' },
  { label: '家庭', value: 'family' },
  { label: '動物', value: 'animals' },
  { label: '自然', value: 'nature' }
]

const batchInput = ref('')
const addedWords = ref([])

// OCR related
const fileInput = ref(null)
const cameraInput = ref(null)
const selectedImage = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const ocrProgress = ref(0)
const ocrResult = ref('')
const isSaving = ref(false)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const triggerCamera = () => {
  cameraInput.value?.click()
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
    selectedImage.value = e.target?.result
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
  ocrProgress.value = 20
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    ocrProgress.value = 50
    
    const response = await $fetch('http://192.168.139.142:3002/ocr/extract-vocab', {
      method: 'POST',
      body: formData
    })
    
    ocrProgress.value = 80
    
    if (response.success && response.vocabulary) {
      // Format: english,chinese per line (removed pinyin)
      ocrResult.value = response.vocabulary
        .map(v => `${v.english || ''},${v.chinese || ''}`)
        .join('\n')
      successMessage.value = '識別成功！'
    } else {
      errorMessage.value = '識別失敗，請重試'
    }
    
    ocrProgress.value = 100
  } catch (error) {
    console.error('OCR error:', error)
    errorMessage.value = 'OCR 處理失敗：' + error.message
  } finally {
    isProcessing.value = false
    ocrProgress.value = 0
  }
}

const addWord = async () => {
  if (!newWord.value.english) {
    errorMessage.value = '請輸入英文'
    return
  }
  
  addedWords.value.push({ ...newWord.value })
  
  // Reset form
  newWord.value = {
    english: '',
    chinese: '',
    category: 'custom'
  }
  
  successMessage.value = '詞語已加入列表'
}

const addBatchWords = () => {
  if (!batchInput.value) return
  
  const lines = batchInput.value.split('\n').filter(line => line.trim())
  
  lines.forEach(line => {
    const parts = line.split(',').map(p => p.trim())
    if (parts[0]) { // At least has english
      addedWords.value.push({
        english: parts[0] || '',
        chinese: parts[1] || '',
        category: 'custom'
      })
    }
  })
  
  batchInput.value = ''
  successMessage.value = `已加入 ${lines.length} 個詞語`
}

const importOCRResult = () => {
  if (!ocrResult.value) return
  
  const lines = ocrResult.value.split('\n').filter(line => line.trim())
  
  lines.forEach(line => {
    const parts = line.split(',').map(p => p.trim())
    if (parts[0]) { // At least has english
      addedWords.value.push({
        english: parts[0] || '',
        chinese: parts[1] || '',
        category: 'ocr'
      })
    }
  })
  
  ocrResult.value = ''
  clearImage()
  successMessage.value = `已匯入 ${lines.length} 個詞語`
}

const removeWord = (index) => {
  addedWords.value.splice(index, 1)
}

const clearAll = () => {
  if (confirm('確定清除所有詞語？')) {
    addedWords.value = []
    successMessage.value = '已清除所有詞語'
  }
}

const saveWords = async () => {
  if (addedWords.value.length === 0) return
  
  isSaving.value = true
  
  try {
    const saved = []
    const skipped = []
    
    for (const word of addedWords.value) {
      try {
        // Check if word exists
        const existing = await $fetch(`http://192.168.139.142:3001/words?english=eq.${word.english}`)
        
        if (existing && existing.length > 0) {
          skipped.push(word.english)
          continue
        }
        
        // Save word
        await $fetch('http://192.168.139.142:3001/words', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation' },
          body: JSON.stringify({
            english: word.english,
            chinese: word.chinese || '',
            pinyin: '', // Empty as per requirement
            category: word.category || 'custom'
          })
        })
        
        saved.push(word.english)
      } catch (error) {
        console.error(`Failed to save ${word.english}:`, error)
      }
    }
    
    // Clear added words
    addedWords.value = []
    
    // Show result
    if (saved.length > 0) {
      successMessage.value = `成功儲存 ${saved.length} 個詞語${skipped.length > 0 ? `（跳過 ${skipped.length} 個重複詞語）` : ''}`
    } else {
      errorMessage.value = '所有詞語已存在'
    }
  } catch (error) {
    console.error('Save error:', error)
    errorMessage.value = '儲存失敗：' + error.message
  } finally {
    isSaving.value = false
  }
}
</script>
