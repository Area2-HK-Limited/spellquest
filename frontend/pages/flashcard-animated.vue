<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl hover:text-amber-600 transition-colors">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-amber-600 animate-bounce-slow">✏️ 中文認字</h1>
        <p class="text-gray-600">翻卡記憶遊戲！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl score-animation">⭐ {{ score }}</div>
        <div class="text-sm text-gray-500">第 {{ currentIndex + 1 }}/{{ words.length }} 題</div>
      </div>
    </div>

    <!-- Game Area -->
    <div v-if="currentWord" class="text-center">
      <!-- Flashcard with 3D flip animation -->
      <div 
        @click="flipCard"
        class="flashcard-container cursor-pointer mb-8"
        style="perspective: 1000px;"
      >
        <div 
          class="flashcard"
          :class="{ 'is-flipped': isFlipped, 'shake-animation': showCorrect === false }"
        >
          <!-- Front Side -->
          <div class="flashcard-face flashcard-front">
            <div class="flex flex-col items-center justify-center h-full">
              <div class="text-8xl mb-4 card-word-animate">{{ currentWord.chinese }}</div>
              <div class="text-2xl text-gray-500">{{ currentWord.pinyin }}</div>
              <UButton 
                @click.stop="speak(currentWord.chinese)" 
                color="warning" 
                variant="outline"
                size="lg"
                class="mt-6 pulse-button"
              >
                🔊 聽發音
              </UButton>
              <p class="text-gray-400 mt-4">點擊翻卡睇英文</p>
            </div>
          </div>

          <!-- Back Side -->
          <div class="flashcard-face flashcard-back">
            <div class="flex flex-col items-center justify-center h-full">
              <div class="text-5xl mb-4 text-amber-600">{{ currentWord.english }}</div>
              <div class="text-3xl text-gray-700">{{ currentWord.chinese }}</div>
              <UButton 
                @click.stop="speak(currentWord.english, 'en-US')" 
                color="warning" 
                variant="outline"
                size="lg"
                class="mt-6 pulse-button"
              >
                🔊 聽英文發音
              </UButton>
              <p class="text-gray-400 mt-4">點擊翻返去</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Celebration overlay for correct answer -->
      <transition name="celebration">
        <div v-if="showCorrect === true" class="celebration-overlay">
          <div class="celebration-content">
            <div class="text-9xl animate-bounce">🎉</div>
            <div class="text-4xl font-bold text-green-600 mt-4">做得好！</div>
          </div>
        </div>
      </transition>

      <!-- Self-assessment -->
      <div class="mb-8">
        <p class="text-xl text-gray-600 mb-4">你識唔識呢個字？</p>
        <div class="flex justify-center gap-4">
          <UButton 
            @click="markAnswer(false)" 
            color="error" 
            size="xl" 
            class="px-8 hover-scale"
          >
            ❌ 唔識
          </UButton>
          <UButton 
            @click="markAnswer(true)" 
            color="success" 
            size="xl" 
            class="px-8 hover-scale"
          >
            ✅ 識！
          </UButton>
        </div>
      </div>
    </div>

    <!-- Completed -->
    <div v-else class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4 animate-bounce">🎉</div>
      <h2 class="text-3xl font-bold text-amber-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-2">你識咗 {{ score }} 個字！</p>
      <p class="text-lg text-gray-500 mb-6">{{ words.length - score }} 個字需要再溫習</p>
      <div class="flex justify-center gap-4">
        <UButton @click="restart" color="warning" size="xl" class="hover-scale">
          再溫習一次
        </UButton>
        <UButton 
          @click="reviewMissed" 
          color="primary" 
          size="xl" 
          v-if="missedWords.length > 0"
          class="hover-scale"
        >
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
const showCorrect = ref(null) // null, true, false

const currentWord = computed(() => {
  return currentIndex.value < words.value.length ? words.value[currentIndex.value] : null
})

const flipCard = () => {
  isFlipped.value = !isFlipped.value
}

const markAnswer = (correct) => {
  showCorrect.value = correct
  
  if (correct) {
    score.value++
    // Play celebration animation for 800ms
    setTimeout(() => {
      showCorrect.value = null
      nextWord()
    }, 800)
  } else {
    missedWords.value.push(currentWord.value)
    // Play shake animation for 500ms
    setTimeout(() => {
      showCorrect.value = null
      nextWord()
    }, 500)
  }
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
  showCorrect.value = null
}

const reviewMissed = () => {
  words.value = [...missedWords.value]
  currentIndex.value = 0
  score.value = 0
  isFlipped.value = false
  missedWords.value = []
  showCorrect.value = null
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

<style scoped>
/* 3D Flashcard flip animation */
.flashcard-container {
  width: 100%;
  height: 400px;
  margin: 0 auto;
}

.flashcard {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard.is-flipped {
  transform: rotateY(180deg);
}

.flashcard-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  background: white;
  padding: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.flashcard-front {
  background: linear-gradient(135deg, #fff 0%, #fef3c7 100%);
}

.flashcard-back {
  background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
  transform: rotateY(180deg);
}

/* Card word entrance animation */
.card-word-animate {
  animation: fadeInScale 0.5s ease-out;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Shake animation for wrong answer */
.shake-animation {
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0) rotateY(0deg); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px) rotateY(5deg); }
  20%, 40%, 60%, 80% { transform: translateX(10px) rotateY(-5deg); }
}

/* Celebration overlay */
.celebration-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(34, 197, 94, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  pointer-events: none;
}

.celebration-content {
  animation: celebrationBounce 0.8s ease-out;
}

@keyframes celebrationBounce {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(100px);
  }
  50% {
    opacity: 1;
    transform: scale(1.1) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.celebration-enter-active, .celebration-leave-active {
  transition: opacity 0.3s;
}

.celebration-enter-from, .celebration-leave-to {
  opacity: 0;
}

/* Pulse button animation */
.pulse-button {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(245, 158, 11, 0);
  }
}

/* Hover scale effect */
.hover-scale {
  transition: transform 0.2s;
}

.hover-scale:hover {
  transform: scale(1.1);
}

/* Score animation */
.score-animation {
  animation: scoreIncrement 0.3s ease-out;
}

@keyframes scoreIncrement {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
    color: #f59e0b;
  }
  100% {
    transform: scale(1);
  }
}

/* Slow bounce for title */
@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-slow {
  animation: bounce-slow 2s infinite;
}
</style>
