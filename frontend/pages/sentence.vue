<template>
  <div class="container mx-auto px-4 py-8 max-w-2xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-green-600">📝 句子重組</h1>
        <p class="text-gray-600">排列正確句子順序！</p>
      </div>
      <div class="text-right">
        <div class="text-2xl">⭐ {{ score }}</div>
        <div class="text-sm text-gray-500">第 {{ currentIndex + 1 }}/{{ sentences.length }} 題</div>
      </div>
    </div>

    <!-- Game Area -->
    <div v-if="currentSentence" class="sq-card bg-white p-8 text-center mb-8">
      <!-- Translation (Hint) -->
      <div class="text-2xl text-gray-700 mb-2">{{ currentSentence.translation }}</div>
      <p class="text-gray-500 mb-6">將下面的詞語排成正確句子</p>
      
      <!-- Speak Button -->
      <UButton 
        @click="speak(currentSentence.content)" 
        color="success" 
        variant="outline"
        size="lg"
        class="mb-6"
      >
        🔊 聽正確答案
      </UButton>

      <!-- Scrambled Words -->
      <div class="mb-6">
        <p class="text-gray-500 mb-3">可用詞語（點擊選擇）：</p>
        <div class="flex flex-wrap justify-center gap-2">
          <UButton
            v-for="(word, index) in scrambledWords"
            :key="index"
            @click="selectWord(index)"
            :disabled="selectedIndexes.includes(index)"
            size="lg"
            :color="selectedIndexes.includes(index) ? 'neutral' : 'success'"
            class="text-lg font-medium"
          >
            {{ word }}
          </UButton>
        </div>
      </div>

      <!-- Answer Area -->
      <div class="mb-6">
        <p class="text-gray-500 mb-3">你的句子：</p>
        <div 
          class="min-h-16 border-2 border-dashed border-gray-300 rounded-xl p-4 flex flex-wrap justify-center gap-2"
          :class="{
            'border-green-500 bg-green-50': feedback === 'correct',
            'border-red-500 bg-red-50': feedback === 'wrong'
          }"
        >
          <UButton
            v-for="(word, index) in answer"
            :key="index"
            @click="removeWord(index)"
            size="lg"
            color="secondary"
            class="text-lg font-medium"
          >
            {{ word }}
          </UButton>
          <span v-if="answer.length === 0" class="text-gray-400 text-lg self-center">
            點擊上面詞語組成句子...
          </span>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="feedback" class="text-2xl font-bold mb-6" :class="feedback === 'correct' ? 'text-green-600' : 'text-red-600'">
        {{ feedback === 'correct' ? '✅ 正確！Great job！' : '❌ 再試一次！' }}
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4">
        <UButton @click="clearAnswer" color="neutral" size="lg">
          清除
        </UButton>
        <UButton @click="checkAnswer" color="success" size="lg" :disabled="answer.length === 0">
          確認答案
        </UButton>
        <UButton v-if="feedback === 'correct'" @click="nextSentence" color="primary" size="lg">
          下一題 →
        </UButton>
      </div>
    </div>

    <!-- Completed -->
    <div v-else class="sq-card bg-white p-8 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h2 class="text-3xl font-bold text-green-600 mb-4">完成！</h2>
      <p class="text-xl text-gray-600 mb-6">你答對了 {{ score }} 題！</p>
      <UButton @click="restart" color="success" size="xl">
        再玩一次
      </UButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Sample sentences
const sentences = ref([
  { content: 'I have a red apple.', translation: '我有一個紅蘋果。' },
  { content: 'The cat is sleeping.', translation: '貓正在睡覺。' },
  { content: 'I go to school.', translation: '我去上學。' },
  { content: 'This is my book.', translation: '這是我的書。' },
  { content: 'I love my family.', translation: '我愛我的家人。' }
])

const currentIndex = ref(0)
const score = ref(0)
const answer = ref([])
const selectedIndexes = ref([])
const feedback = ref(null)

const currentSentence = computed(() => {
  return currentIndex.value < sentences.value.length ? sentences.value[currentIndex.value] : null
})

const scrambledWords = computed(() => {
  if (!currentSentence.value) return []
  const words = currentSentence.value.content.split(' ')
  // Shuffle words
  for (let i = words.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [words[i], words[j]] = [words[j], words[i]]
  }
  return words
})

const selectWord = (index) => {
  if (!selectedIndexes.value.includes(index)) {
    selectedIndexes.value.push(index)
    answer.value.push(scrambledWords.value[index])
    feedback.value = null
  }
}

const removeWord = (index) => {
  const word = answer.value[index]
  answer.value.splice(index, 1)
  const scrambledIndex = scrambledWords.value.findIndex(
    (w, i) => w === word && selectedIndexes.value.includes(i)
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
  const userAnswer = answer.value.join(' ')
  const correctAnswer = currentSentence.value.content
  
  if (userAnswer === correctAnswer) {
    feedback.value = 'correct'
    score.value++
    speak(currentSentence.value.content)
  } else {
    feedback.value = 'wrong'
  }
}

const nextSentence = () => {
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

const speak = (text) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.8
    window.speechSynthesis.speak(utterance)
  }
}
</script>
