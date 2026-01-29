<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-teal-600">🔗 配對遊戲</h1>
        <p class="text-gray-600">中英配對，訓練記憶！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl">⏱️ {{ formatTime(timer) }}</div>
        <div class="text-sm text-gray-500">配對：{{ matchedPairs }}/{{ totalPairs }}</div>
      </div>
    </div>

    <!-- Game Board -->
    <div class="grid grid-cols-4 gap-4 mb-8">
      <div
        v-for="(card, index) in shuffledCards"
        :key="index"
        @click="selectCard(index)"
        class="aspect-square sq-card flex items-center justify-center cursor-pointer transition-all duration-300"
        :class="getCardClass(index)"
      >
        <div v-if="isCardVisible(index)" class="text-center p-2">
          <span class="text-2xl md:text-3xl font-bold">{{ card.text }}</span>
        </div>
        <div v-else class="text-4xl">❓</div>
      </div>
    </div>

    <!-- Game Over -->
    <div v-if="gameComplete" class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h2 class="text-3xl font-bold text-teal-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-2">用時：{{ formatTime(timer) }}</p>
      <p class="text-lg text-gray-500 mb-6">嘗試次數：{{ attempts }}</p>
      <UButton @click="restartGame" color="primary" size="xl">
        再玩一次
      </UButton>
    </div>

    <!-- Instructions -->
    <div class="text-center text-gray-500">
      <p>揭開卡片，搵出中英配對！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const words = [
  { chinese: '蘋果', english: 'apple' },
  { chinese: '香蕉', english: 'banana' },
  { chinese: '橙', english: 'orange' },
  { chinese: '書包', english: 'bag' },
  { chinese: '鉛筆', english: 'pencil' },
  { chinese: '老師', english: 'teacher' },
  { chinese: '學生', english: 'student' },
  { chinese: '太陽', english: 'sun' }
]

const shuffledCards = ref([])
const selectedCards = ref([])
const matchedIndexes = ref([])
const timer = ref(0)
const attempts = ref(0)
const timerInterval = ref(null)

const totalPairs = computed(() => words.length)
const matchedPairs = computed(() => matchedIndexes.value.length / 2)
const gameComplete = computed(() => matchedPairs.value === totalPairs.value)

const initGame = () => {
  // Create pairs of cards
  const cards = []
  words.forEach((word, pairId) => {
    cards.push({ text: word.chinese, pairId, type: 'chinese' })
    cards.push({ text: word.english, pairId, type: 'english' })
  })
  
  // Shuffle cards
  for (let i = cards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [cards[i], cards[j]] = [cards[j], cards[i]]
  }
  
  shuffledCards.value = cards
  selectedCards.value = []
  matchedIndexes.value = []
  timer.value = 0
  attempts.value = 0
  
  // Start timer
  if (timerInterval.value) clearInterval(timerInterval.value)
  timerInterval.value = setInterval(() => {
    if (!gameComplete.value) {
      timer.value++
    }
  }, 1000)
}

const selectCard = (index) => {
  // Don't select if already matched or already selected
  if (matchedIndexes.value.includes(index)) return
  if (selectedCards.value.includes(index)) return
  if (selectedCards.value.length >= 2) return
  
  selectedCards.value.push(index)
  
  // Check for match when 2 cards selected
  if (selectedCards.value.length === 2) {
    attempts.value++
    
    const [first, second] = selectedCards.value
    const card1 = shuffledCards.value[first]
    const card2 = shuffledCards.value[second]
    
    if (card1.pairId === card2.pairId && card1.type !== card2.type) {
      // Match found!
      matchedIndexes.value.push(first, second)
      selectedCards.value = []
      
      // Play success sound
      playSound(true)
      
      // Check if game complete
      if (gameComplete.value) {
        clearInterval(timerInterval.value)
      }
    } else {
      // No match, flip back after delay
      playSound(false)
      setTimeout(() => {
        selectedCards.value = []
      }, 1000)
    }
  }
}

const isCardVisible = (index) => {
  return selectedCards.value.includes(index) || matchedIndexes.value.includes(index)
}

const getCardClass = (index) => {
  if (matchedIndexes.value.includes(index)) {
    return 'bg-green-100 border-2 border-green-500'
  }
  if (selectedCards.value.includes(index)) {
    return 'bg-teal-100 border-2 border-teal-500'
  }
  return 'bg-white hover:bg-gray-50 border-2 border-gray-200'
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const playSound = (success) => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.value = success ? 800 : 300
    oscillator.type = 'sine'
    gainNode.gain.value = 0.2
    
    oscillator.start()
    oscillator.stop(audioContext.currentTime + 0.15)
  } catch (e) {
    console.log('Audio not supported')
  }
}

const restartGame = () => {
  initGame()
}

onMounted(() => {
  initGame()
})

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>
