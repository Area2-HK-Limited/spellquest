<template>
  <UContainer>
    <div class="py-4 sm:py-8">
      <!-- Header -->
      <UPageHeader
        title="🔤 英文串字"
        description="睇中文，串英文！"
      >
        <template #links>
          <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left">返回</UButton>
        </template>
        
        <template #headline>
          <div class="flex items-center justify-between w-full">
            <div></div>
            <div class="flex items-center gap-4">
              <UBadge color="yellow" size="lg" variant="solid">
                <span class="text-lg">⭐ {{ score }}</span>
              </UBadge>
              <UBadge color="gray" size="lg">
                {{ currentIndex + 1 }}/{{ words.length }}
              </UBadge>
            </div>
          </div>
        </template>
      </UPageHeader>

      <!-- Game Area -->
      <UCard v-if="currentWord" class="text-center mb-8">
        <!-- Word Display -->
        <div v-if="currentWord.chinese" class="text-3xl sm:text-5xl mb-2 font-bold text-primary-600">
          {{ currentWord.chinese }}
        </div>
        <div v-else class="text-xl sm:text-3xl mb-2 text-purple-600">
          🔊 聽發音，串英文字
        </div>
        
        <div v-if="currentWord.pinyin" class="text-base sm:text-xl text-gray-500 mb-4 sm:mb-6">
          {{ currentWord.pinyin }}
        </div>
        <div v-else-if="!currentWord.chinese" class="text-sm sm:text-lg text-gray-400 mb-4 sm:mb-6">
          第 {{ currentIndex + 1 }} 個字
        </div>
        
        <!-- Speak Button -->
        <UButton 
          @click="speakWord" 
          color="primary" 
          variant="outline"
          :size="isMobile ? 'md' : 'lg'"
          icon="i-heroicons-speaker-wave"
          class="mb-4 sm:mb-6"
        >
          聽發音
        </UButton>

        <!-- Scrambled Letters -->
        <div class="mb-4 sm:mb-6">
          <p class="text-sm sm:text-base text-gray-600 mb-2 sm:mb-3 font-medium">
            點擊字母拼出英文：
          </p>
          <div class="flex flex-wrap justify-center gap-1.5 sm:gap-2">
            <UButton
              v-for="(letter, index) in scrambledLetters"
              :key="index"
              @click="selectLetter(index)"
              :disabled="selectedIndexes.includes(index)"
              :size="isMobile ? 'lg' : 'xl'"
              :color="selectedIndexes.includes(index) ? 'gray' : 'primary'"
              :variant="selectedIndexes.includes(index) ? 'soft' : 'solid'"
              class="text-xl sm:text-2xl font-bold"
              :class="isMobile ? 'w-12 h-12' : 'w-14 h-14'"
            >
              {{ letter.toUpperCase() }}
            </UButton>
          </div>
        </div>

        <!-- Answer Area -->
        <div class="mb-4 sm:mb-6">
          <p class="text-sm sm:text-base text-gray-600 mb-2 sm:mb-3 font-medium">
            你的答案：
          </p>
          <div 
            class="min-h-14 sm:min-h-16 border-2 border-dashed rounded-xl p-3 sm:p-4 flex flex-wrap justify-center gap-1.5 sm:gap-2 transition-colors"
            :class="{
              'border-gray-300 bg-gray-50': !feedback,
              'border-green-500 bg-green-50': feedback === 'correct',
              'border-red-500 bg-red-50': feedback === 'wrong'
            }"
          >
            <UButton
              v-for="(letter, index) in answer"
              :key="index"
              @click="removeLetter(index)"
              :size="isMobile ? 'lg' : 'xl'"
              color="indigo"
              variant="soft"
              class="text-xl sm:text-2xl font-bold"
              :class="isMobile ? 'w-12 h-12' : 'w-14 h-14'"
            >
              {{ letter.toUpperCase() }}
            </UButton>
            <span v-if="answer.length === 0" class="text-gray-400 text-base sm:text-xl self-center">
              點擊上面字母...
            </span>
          </div>
        </div>

        <!-- Feedback -->
        <div v-if="feedback" class="mb-4 sm:mb-6 space-y-4">
          <UAlert
            v-if="feedback === 'correct'"
            color="green"
            variant="solid"
            title="✅ 正確！太棒了！"
            class="text-lg sm:text-xl"
          />
          <UAlert
            v-else
            color="red"
            variant="solid"
            title="❌ 再試一次！"
            class="text-lg sm:text-xl"
          />
          
          <!-- Memory Tip (shown after correct answer) -->
          <UAlert
            v-if="feedback === 'correct' && memoryTip"
            color="amber"
            variant="subtle"
            icon="i-heroicons-light-bulb"
          >
            <template #title>
              <span class="font-bold">💡 記憶小貼士：</span>
            </template>
            <template #description>
              {{ memoryTip }}
            </template>
          </UAlert>
        </div>

        <!-- Actions -->
        <template #footer>
          <div class="flex flex-col sm:flex-row justify-center gap-2 sm:gap-4">
            <UButton 
              @click="clearAnswer" 
              color="gray" 
              :size="isMobile ? 'md' : 'lg'" 
              icon="i-heroicons-trash"
              class="w-full sm:w-auto"
            >
              清除
            </UButton>
            <UButton 
              @click="checkAnswer" 
              color="primary" 
              :size="isMobile ? 'md' : 'lg'" 
              :disabled="answer.length === 0"
              icon="i-heroicons-check"
              class="w-full sm:w-auto"
            >
              確認答案
            </UButton>
            <UButton 
              v-if="feedback === 'correct'" 
              @click="nextWord" 
              color="green" 
              :size="isMobile ? 'md' : 'lg'"
              icon="i-heroicons-arrow-right"
              class="w-full sm:w-auto"
            >
              下一題
            </UButton>
          </div>
        </template>
      </UCard>

      <!-- Completed -->
      <UCard v-else class="text-center">
        <div class="text-5xl sm:text-6xl mb-4">🎉</div>
        <h2 class="text-2xl sm:text-3xl font-bold text-primary-600 mb-4">完成！</h2>
        <p class="text-lg sm:text-xl text-gray-600 mb-6">你答對了 {{ score }} 題！</p>
        
        <template #footer>
          <div class="flex justify-center">
            <UButton 
              @click="restart" 
              color="primary" 
              :size="isMobile ? 'lg' : 'xl'"
              icon="i-heroicons-arrow-path"
              class="w-full sm:w-auto"
            >
              再玩一次
            </UButton>
          </div>
        </template>
      </UCard>
    </div>
  </UContainer>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

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

// Mobile detection
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 640 // Tailwind sm breakpoint
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
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

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

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
    const selectedIndex = selectedIndexes.value.indexOf(scrambledIndex)
    if (selectedIndex !== -1) {
      selectedIndexes.value.splice(selectedIndex, 1)
    }
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
    memoryTip.value = generateMemoryTip(currentWord.value)
  } else {
    feedback.value = 'wrong'
    memoryTip.value = ''
  }
}

const nextWord = () => {
  currentIndex.value++
  clearAnswer()
  memoryTip.value = ''
}

const restart = () => {
  currentIndex.value = 0
  score.value = 0
  clearAnswer()
  memoryTip.value = ''
}

const speakWord = () => {
  if (!currentWord.value?.english) return
  
  const utterance = new SpeechSynthesisUtterance(currentWord.value.english)
  utterance.lang = 'en-US'
  utterance.rate = 0.8
  window.speechSynthesis.speak(utterance)
}
</script>
