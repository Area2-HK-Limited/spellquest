<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-amber-600">✏️ 中文認字</h1>
        <p class="text-gray-600">翻卡記憶遊戲！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl">⭐ {{ score }}</div>
        <div class="text-sm text-gray-500">第 {{ currentIndex + 1 }}/{{ words.length }} 題</div>
      </div>
    </div>

    <!-- Game Area -->
    <div v-if="currentWord" class="text-center">
      <!-- Flashcard -->
      <div 
        @click="flipCard"
        class="sq-card bg-white p-12 cursor-pointer mb-8 transition-all duration-500 transform hover:scale-105"
        :class="{ 'rotate-y-180': isFlipped }"
        style="min-height: 300px; perspective: 1000px;"
      >
        <div v-if="!isFlipped" class="flex flex-col items-center justify-center h-full">
          <div class="text-8xl mb-4">{{ currentWord.chinese }}</div>
          <div class="text-2xl text-gray-500">{{ currentWord.pinyin }}</div>
          <UButton 
            @click.stop="speak(currentWord.chinese)" 
            color="warning" 
            variant="outline"
            size="lg"
            class="mt-6"
          >
            🔊 聽發音
          </UButton>
          <p class="text-gray-400 mt-4">點擊翻卡睇英文</p>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full">
          <div class="text-5xl mb-4 text-amber-600">{{ currentWord.english }}</div>
          <div class="text-3xl text-gray-700">{{ currentWord.chinese }}</div>
          <UButton 
            @click.stop="speak(currentWord.english, 'en-US')" 
            color="warning" 
            variant="outline"
            size="lg"
            class="mt-6"
          >
            🔊 聽英文發音
          </UButton>
          <p class="text-gray-400 mt-4">點擊翻返去</p>
        </div>
      </div>

      <!-- Self-assessment -->
      <div class="mb-8">
        <p class="text-xl text-gray-600 mb-4">你識唔識呢個字？</p>
        <div class="flex justify-center gap-4">
          <UButton @click="markAnswer(false)" color="error" size="xl" class="px-8">
            ❌ 唔識
          </UButton>
          <UButton @click="markAnswer(true)" color="success" size="xl" class="px-8">
            ✅ 識！
          </UButton>
        </div>
      </div>
    </div>

    <!-- Completed -->
    <div v-else class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h2 class="text-3xl font-bold text-amber-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-2">你識咗 {{ score }} 個字！</p>
      <p class="text-lg text-gray-500 mb-6">{{ words.length - score }} 個字需要再溫習</p>
      <div class="flex justify-center gap-4">
        <UButton @click="restart" color="warning" size="xl">
          再溫習一次
        </UButton>
        <UButton @click="reviewMissed" color="primary" size="xl" v-if="missedWords.length > 0">
          只溫習唔識嘅
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Sample words
const allWords = [
  { chinese: '蘋果', english: 'apple', pinyin: 'píng guǒ' },
  { chinese: '香蕉', english: 'banana', pinyin: 'xiāng jiāo' },
  { chinese: '橙', english: 'orange', pinyin: 'chéng' },
  { chinese: '書包', english: 'school bag', pinyin: 'shū bāo' },
  { chinese: '鉛筆', english: 'pencil', pinyin: 'qiān bǐ' },
  { chinese: '老師', english: 'teacher', pinyin: 'lǎo shī' },
  { chinese: '學生', english: 'student', pinyin: 'xué shēng' },
  { chinese: '爸爸', english: 'father', pinyin: 'bà ba' },
  { chinese: '媽媽', english: 'mother', pinyin: 'mā ma' },
  { chinese: '太陽', english: 'sun', pinyin: 'tài yáng' }
]

const words = ref([...allWords])
const currentIndex = ref(0)
const score = ref(0)
const isFlipped = ref(false)
const missedWords = ref([])

const currentWord = computed(() => {
  return currentIndex.value < words.value.length ? words.value[currentIndex.value] : null
})

const flipCard = () => {
  isFlipped.value = !isFlipped.value
}

const markAnswer = (correct) => {
  if (correct) {
    score.value++
  } else {
    missedWords.value.push(currentWord.value)
  }
  nextWord()
}

const nextWord = () => {
  currentIndex.value++
  isFlipped.value = false
}

const restart = () => {
  words.value = [...allWords]
  currentIndex.value = 0
  score.value = 0
  isFlipped.value = false
  missedWords.value = []
}

const reviewMissed = () => {
  words.value = [...missedWords.value]
  currentIndex.value = 0
  score.value = 0
  isFlipped.value = false
  missedWords.value = []
}

const speak = (text, lang = 'zh-TW') => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 0.8
    window.speechSynthesis.speak(utterance)
  }
}
</script>
