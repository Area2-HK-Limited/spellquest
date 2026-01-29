<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-cyan-600">📚 詞語列表</h1>
        <p class="text-gray-600">所有詞語一覽</p>
      </div>
      <NuxtLink to="/input">
        <UButton color="primary">➕ 新增</UButton>
      </NuxtLink>
    </div>

    <!-- Filter -->
    <div class="sq-card bg-white p-4 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <UInput 
          v-model="searchQuery" 
          placeholder="搜尋詞語..." 
          icon="i-heroicons-magnifying-glass"
          class="flex-1"
        />
        <USelect v-model="filterCategory" :options="categoryOptions" placeholder="分類" />
      </div>
    </div>

    <!-- Word List -->
    <div class="sq-card bg-white overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-4 text-left text-sm font-semibold text-gray-600">中文</th>
            <th class="px-6 py-4 text-left text-sm font-semibold text-gray-600">英文</th>
            <th class="px-6 py-4 text-left text-sm font-semibold text-gray-600">拼音</th>
            <th class="px-6 py-4 text-left text-sm font-semibold text-gray-600">分類</th>
            <th class="px-6 py-4 text-center text-sm font-semibold text-gray-600">發音</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="word in filteredWords" 
            :key="word.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-6 py-4 text-xl font-bold text-cyan-600">{{ word.chinese }}</td>
            <td class="px-6 py-4 text-gray-700">{{ word.english }}</td>
            <td class="px-6 py-4 text-gray-500">{{ word.pinyin }}</td>
            <td class="px-6 py-4">
              <UBadge :color="getCategoryColor(word.category)">{{ word.category }}</UBadge>
            </td>
            <td class="px-6 py-4 text-center">
              <UButton 
                @click="speak(word.chinese)" 
                color="primary" 
                variant="ghost" 
                size="sm"
              >
                🔊
              </UButton>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredWords.length === 0" class="p-8 text-center text-gray-500">
        冇搵到詞語
      </div>
    </div>

    <!-- Stats -->
    <div class="mt-6 text-center text-gray-500">
      共 {{ filteredWords.length }} 個詞語
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const words = ref([
  { id: 1, chinese: '蘋果', english: 'apple', pinyin: 'píng guǒ', category: 'fruit' },
  { id: 2, chinese: '香蕉', english: 'banana', pinyin: 'xiāng jiāo', category: 'fruit' },
  { id: 3, chinese: '橙', english: 'orange', pinyin: 'chéng', category: 'fruit' },
  { id: 4, chinese: '書包', english: 'school bag', pinyin: 'shū bāo', category: 'school' },
  { id: 5, chinese: '鉛筆', english: 'pencil', pinyin: 'qiān bǐ', category: 'school' },
  { id: 6, chinese: '老師', english: 'teacher', pinyin: 'lǎo shī', category: 'school' },
  { id: 7, chinese: '學生', english: 'student', pinyin: 'xué shēng', category: 'school' },
  { id: 8, chinese: '爸爸', english: 'father', pinyin: 'bà ba', category: 'family' },
  { id: 9, chinese: '媽媽', english: 'mother', pinyin: 'mā ma', category: 'family' },
  { id: 10, chinese: '太陽', english: 'sun', pinyin: 'tài yáng', category: 'nature' }
])

const searchQuery = ref('')
const filterCategory = ref('')

const categoryOptions = [
  { label: '全部', value: '' },
  { label: '水果', value: 'fruit' },
  { label: '學校', value: 'school' },
  { label: '家庭', value: 'family' },
  { label: '自然', value: 'nature' }
]

const filteredWords = computed(() => {
  return words.value.filter(word => {
    const matchesSearch = !searchQuery.value || 
      word.chinese.includes(searchQuery.value) ||
      word.english.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      word.pinyin.includes(searchQuery.value)
    
    const matchesCategory = !filterCategory.value || word.category === filterCategory.value
    
    return matchesSearch && matchesCategory
  })
})

const getCategoryColor = (category) => {
  const colors = {
    fruit: 'success',
    school: 'primary',
    family: 'warning',
    nature: 'info',
    general: 'neutral'
  }
  return colors[category] || 'neutral'
}

const speak = (text) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-TW'
    utterance.rate = 0.8
    window.speechSynthesis.speak(utterance)
  }
}
</script>
