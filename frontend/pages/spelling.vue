<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-indigo-600">🔤 英文串字</h1>
        <p class="text-gray-600">睇中文，串英文！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl">⭐ {{ score }}</div>
        <div class="text-sm text-gray-500">第 {{ currentIndex + 1 }}/{{ words.length }} 題</div>
      </div>
    </div>

    <!-- Game Area -->
    <div v-if="currentWord" class="sq-card bg-white p-8 text-center mb-8">
      <!-- Chinese Word -->
      <div class="text-5xl mb-2">{{ currentWord.chinese }}</div>
      <div class="text-xl text-gray-500 mb-6">{{ currentWord.pinyin }}</div>
      
      <!-- Speak Button -->
      <UButton 
        @click="speak(currentWord.chinese)" 
        color="primary" 
        variant="outline"
        size="lg"
        class="mb-6"
      >
        🔊 聽發音
      </UButton>

      <!-- Scrambled Letters -->
      <div class="mb-6">
        <p class="text-gray-500 mb-3">點擊字母拼出英文：</p>
        <div class="flex flex-wrap justify-center gap-2">
          <UButton
            v-for="(letter, index) in scrambledLetters"
            :key="index"
            @click="selectLetter(index)"
            :disabled="selectedIndexes.includes(index)"
            size="xl"
            :color="selectedIndexes.includes(index) ? 'neutral' : 'primary'"
            class="text-2xl w-14 h-14 font-bold"
          >
            {{ letter }}
          </UButton>
        </div>
      </div>

      <!-- Answer Area -->
      <div class="mb-6">
        <p class="text-gray-500 mb-3">你的答案：</p>
        <div 
          class="min-h-16 border-2 border-dashed border-gray-300 rounded-xl p-4 flex flex-wrap justify-center gap-2"
          :class="{
            'border-green-500 bg-green-50': feedback === 'correct',
            'border-red-500 bg-red-50': feedback === 'wrong'
          }"
        >
          <UButton
            v-for="(letter, index) in answer"
            :key="index"
            @click="removeLetter(index)"
            size="xl"
            color="secondary"
            class="text-2xl w-14 h-14 font-bold"
          >
            {{ letter }}
          </UButton>
          <span v-if="answer.length === 0" class="text-gray-400 text-xl self-center">
            點擊上面字母...
          </span>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="feedback" class="text-2xl font-bold mb-6" :class="feedback === 'correct' ? 'text-green-600' : 'text-red-600'">
        {{ feedback === 'correct' ? '✅ 正確！太棒了！' : '❌ 再試一次！' }}
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4">
        <UButton @click="clearAnswer" color="neutral" size="lg">
          清除
        </UButton>
        <UButton @click="checkAnswer" color="primary" size="lg" :disabled="answer.length === 0">
          確認答案
        </UButton>
        <UButton v-if="feedback === 'correct'" @click="nextWord" color="success" size="lg">
          下一題 →
        </UButton>
      </div>
    </div>

    <!-- Completed -->
    <div v-else class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h2 class="text-3xl font-bold text-indigo-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-6">你答對了 {{ score }} 題！</p>
      <UButton @click="restart" color="primary" size="xl">
        再玩一次
      </UButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Sample words (will be loaded from API later)
const words = ref([
  { chinese: '蘋果', english: 'apple', pinyin: 'píng guǒ' },
  { chinese: '香蕉', english: 'banana', pinyin: 'xiāng jiāo' },
  { chinese: '橙', english: 'orange', pinyin: 'chéng' },
  { chinese: '書包', english: 'schoolbag', pinyin: 'shū bāo' },
  { chinese: '鉛筆', english: 'pencil', pinyin: 'qiān bǐ' }
])

const currentIndex = ref(0)
const score = ref(0)
const answer = ref([])
const selectedIndexes = ref([])
const feedback = ref(null)

const currentWord = computed(() => {
  return currentIndex.value < words.value.length ? words.value[currentIndex.value] : null
})

const scrambledLetters = computed(() => {
  if (!currentWord.value) return []
  const letters = currentWord.value.english.split('')
  // Shuffle letters
  for (let i = letters.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [letters[i], letters[j]] = [letters[j], letters[i]]
  }
  return letters
})

const selectLetter = (index) => {
  if (!selectedIndexes.value.includes(index)) {
    selectedIndexes.value.push(index)
    answer.value.push(scrambledLetters.value[index])
    feedback.value = null
  }
}

const removeLetter = (index) => {
  const letter = answer.value[index]
  answer.value.splice(index, 1)
  // Find and remove from selectedIndexes
  const scrambledIndex = scrambledLetters.value.findIndex(
    (l, i) => l === letter && selectedIndexes.value.includes(i)
  )
  if (scrambledIndex !== -1) {
    selectedIndexes.value = selectedIndexes.value.filter(i => i !== scrambledIndex)
  }
  feedback.value = null
}

const clearAnswer = () => {
  answer.value = []
  selectedIndexes.value = []
  feedback.value = null
}

const checkAnswer = () => {
  const userAnswer = answer.value.join('').toLowerCase()
  const correctAnswer = currentWord.value.english.toLowerCase()
  
  if (userAnswer === correctAnswer) {
    feedback.value = 'correct'
    score.value++
    // Speak the word
    speak(currentWord.value.english, 'en-US')
  } else {
    feedback.value = 'wrong'
  }
}

const nextWord = () => {
  currentIndex.value++
  answer.value = []
  selectedIndexes.value = []
  feedback.value = null
}

const restart = () => {
  currentIndex.value = 0
  score.value = 0
  answer.value = []
  selectedIndexes.value = []
  feedback.value = null
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
