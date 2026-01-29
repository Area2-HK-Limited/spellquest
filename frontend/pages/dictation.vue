<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-pink-600">🎯 聽寫模式</h1>
        <p class="text-gray-600">聽發音，寫出正確答案！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl">⭐ {{ score }}</div>
        <div class="text-sm text-gray-500">第 {{ currentIndex + 1 }}/{{ words.length }} 題</div>
      </div>
    </div>

    <!-- Game Area -->
    <div v-if="currentWord" class="sq-card bg-white p-8 text-center mb-8">
      <!-- Play Sound Button -->
      <div class="mb-8">
        <UButton 
          @click="playSound" 
          color="pink" 
          size="xl"
          class="text-4xl p-8 rounded-full"
        >
          🔊
        </UButton>
        <p class="text-gray-500 mt-4">點擊播放發音（可重複聽）</p>
        <p class="text-sm text-gray-400">已播放 {{ playCount }} 次</p>
      </div>

      <!-- Hint (optional) -->
      <div v-if="showHint" class="mb-6 p-4 bg-amber-50 rounded-xl">
        <p class="text-amber-700">💡 提示：{{ currentWord.pinyin }}</p>
      </div>

      <!-- Input Area -->
      <div class="mb-6">
        <p class="text-gray-500 mb-3">寫出你聽到嘅{{ mode === 'chinese' ? '中文' : '英文' }}：</p>
        <UInput 
          v-model="userAnswer"
          :placeholder="mode === 'chinese' ? '輸入中文...' : 'Type English...'"
          size="xl"
          class="text-center text-2xl"
          @keyup.enter="checkAnswer"
        />
      </div>

      <!-- Feedback -->
      <div v-if="feedback" class="mb-6">
        <div 
          class="text-2xl font-bold p-4 rounded-xl"
          :class="feedback === 'correct' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'"
        >
          <template v-if="feedback === 'correct'">
            ✅ 正確！{{ currentWord.chinese }} = {{ currentWord.english }}
          </template>
          <template v-else>
            ❌ 再試一次！
            <span v-if="attempts >= 3" class="block text-lg mt-2">
              答案：{{ mode === 'chinese' ? currentWord.chinese : currentWord.english }}
            </span>
          </template>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4">
        <UButton 
          v-if="!showHint && feedback !== 'correct'" 
          @click="showHint = true" 
          color="warning" 
          variant="outline"
          size="lg"
        >
          💡 提示
        </UButton>
        <UButton 
          @click="checkAnswer" 
          color="pink" 
          size="lg" 
          :disabled="!userAnswer.trim()"
        >
          確認答案
        </UButton>
        <UButton 
          v-if="feedback === 'correct'" 
          @click="nextWord" 
          color="success" 
          size="lg"
        >
          下一題 →
        </UButton>
      </div>
    </div>

    <!-- Completed -->
    <div v-else class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h2 class="text-3xl font-bold text-pink-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-2">你答對了 {{ score }} 題！</p>
      <p class="text-lg text-gray-500 mb-6">正確率：{{ Math.round(score / words.length * 100) }}%</p>
      <div class="flex justify-center gap-4">
        <UButton @click="restart" color="pink" size="xl">
          再練習一次
        </UButton>
        <NuxtLink to="/">
          <UButton color="neutral" size="xl">
            返回主頁
          </UButton>
        </NuxtLink>
      </div>
    </div>

    <!-- Mode Toggle -->
    <div class="mt-8 text-center">
      <p class="text-gray-500 mb-2">練習模式：</p>
      <div class="flex justify-center gap-2">
        <UButton 
          @click="mode = 'chinese'" 
          :color="mode === 'chinese' ? 'pink' : 'neutral'"
          size="sm"
        >
          聽英文寫中文
        </UButton>
        <UButton 
          @click="mode = 'english'" 
          :color="mode === 'english' ? 'pink' : 'neutral'"
          size="sm"
        >
          聽中文寫英文
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const words = ref([
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
])

const mode = ref('chinese') // 'chinese' = 聽英文寫中文, 'english' = 聽中文寫英文
const currentIndex = ref(0)
const score = ref(0)
const userAnswer = ref('')
const feedback = ref(null)
const showHint = ref(false)
const playCount = ref(0)
const attempts = ref(0)

const currentWord = computed(() => {
  return currentIndex.value < words.value.length ? words.value[currentIndex.value] : null
})

const playSound = () => {
  if (!currentWord.value) return
  
  const text = mode.value === 'chinese' ? currentWord.value.english : currentWord.value.chinese
  const lang = mode.value === 'chinese' ? 'en-US' : 'zh-TW'
  
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = 0.7
    window.speechSynthesis.speak(utterance)
    playCount.value++
  }
}

const checkAnswer = () => {
  if (!userAnswer.value.trim()) return
  
  const correctAnswer = mode.value === 'chinese' 
    ? currentWord.value.chinese 
    : currentWord.value.english.toLowerCase()
  
  const userInput = userAnswer.value.trim().toLowerCase()
  
  if (userInput === correctAnswer.toLowerCase()) {
    feedback.value = 'correct'
    score.value++
    // Play success sound
    playSuccessSound()
  } else {
    feedback.value = 'wrong'
    attempts.value++
  }
}

const playSuccessSound = () => {
  // Simple beep using Web Audio API
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.value = 800
    oscillator.type = 'sine'
    gainNode.gain.value = 0.3
    
    oscillator.start()
    oscillator.stop(audioContext.currentTime + 0.15)
  } catch (e) {
    console.log('Audio not supported')
  }
}

const nextWord = () => {
  currentIndex.value++
  userAnswer.value = ''
  feedback.value = null
  showHint.value = false
  playCount.value = 0
  attempts.value = 0
}

const restart = () => {
  currentIndex.value = 0
  score.value = 0
  userAnswer.value = ''
  feedback.value = null
  showHint.value = false
  playCount.value = 0
  attempts.value = 0
}

// Auto-play sound when word changes
watch(currentIndex, () => {
  if (currentWord.value) {
    setTimeout(playSound, 500)
  }
})
</script>
