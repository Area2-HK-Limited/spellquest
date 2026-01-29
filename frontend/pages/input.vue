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

    <!-- OCR Input (Coming Soon) -->
    <div class="sq-card bg-white p-8 mb-8 opacity-60">
      <h2 class="text-xl font-bold text-gray-700 mb-4">📷 OCR 相片輸入</h2>
      <p class="text-gray-500 mb-4">影相上傳溫習範圍，AI 自動識別文字</p>
      
      <div class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center">
        <div class="text-4xl mb-2">📸</div>
        <p class="text-gray-500">Coming Soon...</p>
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
