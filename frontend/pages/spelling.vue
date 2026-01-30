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
      <!-- Word Display -->
      <div v-if="currentWord.chinese" class="text-5xl mb-2">{{ currentWord.chinese }}</div>
      <div v-else class="text-3xl mb-2 text-purple-600">🔊 聽發音，串英文字</div>
      <div v-if="currentWord.pinyin" class="text-xl text-gray-500 mb-6">{{ currentWord.pinyin }}</div>
      <div v-else-if="!currentWord.chinese" class="text-lg text-gray-400 mb-6">第 {{ currentIndex + 1 }} 個字</div>
      
      <!-- Speak Button -->
      <UButton 
        @click="speakWord" 
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
      <div v-if="feedback" class="mb-6">
        <div class="text-2xl font-bold" :class="feedback === 'correct' ? 'text-green-600' : 'text-red-600'">
          {{ feedback === 'correct' ? '✅ 正確！太棒了！' : '❌ 再試一次！' }}
        </div>
        
        <!-- Memory Tip (shown after correct answer) -->
        <div v-if="feedback === 'correct' && memoryTip" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-left">
          <div class="flex items-start gap-2">
            <span class="text-2xl">💡</span>
            <div>
              <p class="font-bold text-yellow-700 mb-1">記憶小貼士：</p>
              <p class="text-yellow-800">{{ memoryTip }}</p>
            </div>
          </div>
        </div>
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

// Default sample words
const defaultWords = [
  { chinese: '蘋果', english: 'apple', pinyin: 'píng guǒ' },
  { chinese: '香蕉', english: 'banana', pinyin: 'xiāng jiāo' },
  { chinese: '橙', english: 'orange', pinyin: 'chéng' },
  { chinese: '書包', english: 'schoolbag', pinyin: 'shū bāo' },
  { chinese: '鉛筆', english: 'pencil', pinyin: 'qiān bǐ' }
]

const words = ref([])
const practiceMode = ref('default')

const currentIndex = ref(0)
const score = ref(0)
const answer = ref([])
const selectedIndexes = ref([])
const feedback = ref(null)
const memoryTip = ref('')

// Memory tips for common words (can be expanded or replaced with AI)
const memoryTips = {
  // Common English words with memory tricks
  'you': '你 (you) - 發音似「優」，你係最優秀嘅！',
  'doing': 'do + ing = doing（正在做）- 記住 do 加 ing 就係進行式！',
  'talking': 'talk + ing = talking（正在講）- talk 講嘢，加 ing 就係講緊嘢',
  'reading': 'read + ing = reading（正在讀）- read 讀書，雙 e 要記住！',
  'book': '書 - b-o-o-k，兩個 o 好似兩隻眼睇書 👀📖',
  'running': 'run + n + ing = running - 跑步要雙寫 n！因為跑得好快 🏃',
  'grass': 'gr + ass = grass（草）- 記住雙 s，草地好大片！',
  'chatting': 'chat + t + ing = chatting - 傾偈要雙 t，因為兩個人傾！',
  'riding': 'ride + ing = riding（踩緊）- 去掉 e 加 ing',
  'bicycle': 'bi（二）+ cycle（圈）= 兩個轆！🚲',
  'her': '佢（女）- h-e-r，三個字母，簡單易記！',
  'sister': 'sis + ter = sister（姊妹）- sis 似「姐」嘅音',
  'swimming': 'swim + m + ing = swimming - 游水要雙 m，因為雙手划水 🏊',
  'pool': 'p-oo-l，兩個 o 好似泳池嘅水 💧',
  'having': 'have + ing = having - 去掉 e 加 ing',
  'fun': '好玩 - f-u-n，三個字母，fun fun fun！🎉',
  'apple': 'a-p-p-l-e，兩個 p 好似蘋果嘅兩邊 🍎',
  'banana': 'b-a-n-a-n-a，三個 a 好似三個香蕉彎彎 🍌',
  'orange': 'or + ange = orange，橙色同橙都係呢個字！🍊'
}

// Generate memory tip for current word
const generateMemoryTip = (word) => {
  const english = word.english?.toLowerCase()
  
  // Check if we have a preset tip
  if (english && memoryTips[english]) {
    return memoryTips[english]
  }
  
  // Generate basic tip based on word structure
  if (english) {
    const tips = []
    
    // Check for -ing words
    if (english.endsWith('ing')) {
      const base = english.slice(0, -3)
      tips.push(`${base} + ing = ${english}（進行式）`)
    }
    
    // Check for double letters
    const doubles = english.match(/(.)\1/g)
    if (doubles) {
      tips.push(`注意雙字母：${doubles.join(', ')}`)
    }
    
    // Word length tip
    if (english.length <= 4) {
      tips.push(`只有 ${english.length} 個字母，簡單易記！`)
    }
    
    // Spelling it out
    tips.push(`拼法：${english.split('').join('-').toUpperCase()}`)
    
    return tips.join(' | ')
  }
  
  return ''
}

// Load words on mount
onMounted(() => {
  // Check if there are custom practice words
  const customWords = localStorage.getItem('spellquest_practice_words')
  const mode = localStorage.getItem('spellquest_practice_mode')
  
  if (mode === 'custom' && customWords) {
    try {
      const parsed = JSON.parse(customWords)
      // Filter words that have english (for spelling game)
      const validWords = parsed.filter(w => w.english && w.english.trim())
      if (validWords.length > 0) {
        words.value = validWords
        practiceMode.value = 'custom'
        // Clear the practice mode flag (one-time use)
        localStorage.removeItem('spellquest_practice_mode')
        return
      }
    } catch (e) {
      console.error('Failed to parse custom words:', e)
    }
  }
  
  // Fall back to default words
  words.value = defaultWords
})

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
    // Generate memory tip
    memoryTip.value = generateMemoryTip(currentWord.value)
    // Speak the word
    speak(currentWord.value.english, 'en-US')
  } else {
    feedback.value = 'wrong'
    memoryTip.value = ''
  }
}

const nextWord = () => {
  currentIndex.value++
  answer.value = []
  selectedIndexes.value = []
  feedback.value = null
  memoryTip.value = ''
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

const speakWord = () => {
  if (!currentWord.value) return
  // For English-only words, speak English; otherwise speak Chinese
  if (currentWord.value.chinese) {
    speak(currentWord.value.chinese, 'zh-TW')
  } else {
    speak(currentWord.value.english, 'en-US')
  }
}
</script>
