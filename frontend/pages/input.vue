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
      <p class="text-gray-700 mb-4">每行一個詞語，格式：中文,英文,拼音</p>
      
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
      <p class="text-gray-700 mb-4">影相或上傳溫習範圍，AI 自動識別文字</p>
      
      <!-- Upload Area -->
      <div 
        class="border-2 border-dashed rounded-xl p-8 text-center transition-all"
        :class="isDragging ? 'border-purple-500 bg-purple-50' : 'border-gray-300'"
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
          <p class="text-sm text-gray-600">支援 JPG、PNG 格式</p>
          <div class="mt-4 flex justify-center gap-4">
            <UButton color="purple" size="lg" @click="triggerFileInput">
              📁 選擇相片
            </UButton>
            <UButton color="purple" variant="outline" size="lg" @click="triggerCamera">
              📷 影相
            </UButton>
          </div>
        </div>
        
        <div v-else class="space-y-4">
          <img :src="selectedImage" class="max-h-64 mx-auto rounded-lg shadow-lg" />
          <div class="flex justify-center gap-4">
            <UButton color="purple" size="lg" @click="processOCR" :loading="isProcessing">
              {{ isProcessing ? '識別中...' : '🔍 開始識別' }}
            </UButton>
            <UButton color="neutral" variant="outline" size="lg" @click="clearImage">
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
        <p class="text-sm text-gray-700 mb-4">
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
      
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div 
          v-for="(word, index) in addedWords" 
          :key="index"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div>
            <span class="text-xl font-bold text-purple-600">{{ word.english || word.chinese }}</span>
            <span v-if="word.chinese && word.english" class="text-gray-700 ml-2">{{ word.chinese }}</span>
            <span v-if="word.pinyin" class="text-gray-600 ml-2 text-sm">({{ word.pinyin }})</span>
          </div>
          <UButton @click="removeWord(index)" color="error" variant="ghost" size="sm">
            ✕
          </UButton>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="mt-6 space-y-4">
        <!-- Start Practice -->
        <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-4">
          <h3 class="font-bold text-purple-700 mb-3">🎮 開始練習</h3>
          <div class="grid grid-cols-2 gap-3">
            <UButton @click="startGame('spelling')" color="purple" size="lg" block>
              🔤 英文串字
            </UButton>
            <UButton @click="startGame('dictation')" color="purple" size="lg" block>
              🎯 聽寫模式
            </UButton>
            <UButton @click="startGame('sentence')" color="purple" variant="outline" size="lg" block>
              📝 句子重組
            </UButton>
            <UButton @click="startGame('matching')" color="purple" variant="outline" size="lg" block>
              🔗 配對遊戲
            </UButton>
          </div>
        </div>
        
        <!-- Save/Clear -->
        <div class="flex gap-4">
          <UButton @click="saveWords" color="success" size="lg">
            💾 儲存詞語
          </UButton>
          <UButton @click="clearAll" color="neutral" size="lg">
            清除全部
          </UButton>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

// Toast notification helper
const showToast = (message) => {
  // Simple alert for now - can be replaced with proper toast library
  // TODO: Replace with UNotification or vue-toastification
  alert(message)
}

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
const cameraInput = ref(null)
const selectedImage = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isProcessing = ref(false)
const ocrResult = ref('')

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
    
    const ocrApiUrl = '/api'
    
    try {
      const response = await fetch(`${ocrApiUrl}/ocr`, {
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
  if (!ocrResult.value.trim()) {
    alert('❌ 未有識別結果')
    return
  }
  
  const lines = ocrResult.value.trim().split('\n')
  let importCount = 0
  let skippedCount = 0
  
  for (const line of lines) {
    // 跳過註釋行
    if (line.startsWith('#')) {
      skippedCount++
      continue
    }
    if (!line.trim()) {
      skippedCount++
      continue
    }
    
    const parts = line.split(',').map(p => p.trim())
    
    // 支援多種格式：
    // 1. 中文,英文,拼音 (原有格式)
    // 2. 英文 (只有英文單詞)
    // 3. 英文,中文 (英文在前)
    
    if (parts.length === 1) {
      // 只有一個詞
      const word = parts[0]
      if (!word) {
        skippedCount++
        continue
      }
      const isEnglish = /^[a-zA-Z\s]+$/.test(word)
      addedWords.value.push({
        chinese: isEnglish ? '' : word,
        english: isEnglish ? word : '',
        pinyin: '',
        category: 'custom'
      })
      importCount++
    } else if (parts.length >= 2) {
      // 判斷第一個係中文定英文
      const first = parts[0]
      const second = parts[1]
      if (!first && !second) {
        skippedCount++
        continue
      }
      const isFirstEnglish = /^[a-zA-Z\s]+$/.test(first)
      
      addedWords.value.push({
        chinese: isFirstEnglish ? second : first,
        english: isFirstEnglish ? first : second,
        pinyin: parts[2] || '',
        category: 'custom'
      })
      importCount++
    }
  }
  
  if (importCount > 0) {
    showToast(`✅ 已匯入 ${importCount} 個詞語${skippedCount > 0 ? `，跳過 ${skippedCount} 行` : ''}！`)
    ocrResult.value = ''
    selectedImage.value = null
    selectedFile.value = null
  } else {
    alert('❌ 無法匯入任何詞語，請檢查格式')
  }
}

const addWord = () => {
  // Validation: at least one of chinese or english must be filled
  if (!newWord.value.chinese.trim() && !newWord.value.english.trim()) {
    alert('請輸入中文或英文！')
    return
  }
  
  addedWords.value.push({ ...newWord.value })
  
  // Success feedback
  const wordDisplay = newWord.value.english || newWord.value.chinese
  showToast(`✅ 已新增詞語：${wordDisplay}`)
  
  // Reset form
  newWord.value = {
    chinese: '',
    english: '',
    pinyin: '',
    category: 'general'
  }
}

const addBatchWords = () => {
  if (!batchInput.value.trim()) {
    alert('請輸入詞語！')
    return
  }
  
  const lines = batchInput.value.trim().split('\n')
  let importCount = 0
  let skippedCount = 0
  
  for (const line of lines) {
    if (!line.trim()) continue
    
    const parts = line.split(',').map(p => p.trim())
    
    if (parts.length === 1) {
      // 只有一個詞 - 判斷係中文定英文
      const word = parts[0]
      if (!word) {
        skippedCount++
        continue
      }
      const isEnglish = /^[a-zA-Z\s]+$/.test(word)
      addedWords.value.push({
        chinese: isEnglish ? '' : word,
        english: isEnglish ? word : '',
        pinyin: '',
        category: 'custom'
      })
      importCount++
    } else if (parts[0]) {
      // 多個 parts - 判斷格式
      const first = parts[0]
      const second = parts[1] || ''
      const isFirstEnglish = /^[a-zA-Z\s]+$/.test(first)
      
      addedWords.value.push({
        chinese: isFirstEnglish ? second : first,
        english: isFirstEnglish ? first : second,
        pinyin: parts[2] || '',
        category: 'custom'
      })
      importCount++
    }
  }
  
  if (importCount > 0) {
    showToast(`✅ 已批量新增 ${importCount} 個詞語${skippedCount > 0 ? `，跳過 ${skippedCount} 行` : ''}！`)
    batchInput.value = ''
  } else {
    alert('❌ 無法識別任何詞語，請檢查格式')
  }
}

const removeWord = (index) => {
  const word = addedWords.value[index]
  const wordDisplay = word.english || word.chinese
  addedWords.value.splice(index, 1)
  showToast(`🗑️ 已刪除：${wordDisplay}`)
}

const clearAll = () => {
  if (addedWords.value.length === 0) return
  
  if (confirm(`確定要清除全部 ${addedWords.value.length} 個詞語？`)) {
    addedWords.value = []
    showToast('🗑️ 已清除全部詞語')
  }
}

const saveWords = async () => {
  if (addedWords.value.length === 0) {
    alert('❌ 未有詞語可儲存')
    return
  }
  
  // Save to localStorage for persistence
  localStorage.setItem('spellquest_custom_words', JSON.stringify(addedWords.value))
  showToast(`💾 已儲存 ${addedWords.value.length} 個詞語！`)
}

const startGame = (gameType) => {
  if (addedWords.value.length === 0) {
    alert('❌ 請先新增詞語！')
    return
  }
  
  // Save words to localStorage for the game to use
  localStorage.setItem('spellquest_practice_words', JSON.stringify(addedWords.value))
  localStorage.setItem('spellquest_practice_mode', 'custom')
  
  showToast(`🎮 開始遊戲：${gameType}`)
  
  // Navigate to game
  navigateTo(`/${gameType}`)
}
</script>
