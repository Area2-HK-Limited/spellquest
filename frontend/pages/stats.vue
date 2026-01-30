<template>
  <div class="container mx-auto px-4 py-8 max-w-6xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl hover:text-amber-600 transition-colors">← 返回</NuxtLink>
      <h1 class="text-4xl font-bold text-amber-600">📊 學習統計</h1>
      <div class="w-20"></div> <!-- Spacer for centering -->
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20">
      <div class="text-6xl mb-4">⏳</div>
      <p class="text-xl text-gray-600">載入中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div class="text-4xl mb-4">⚠️</div>
      <p class="text-red-600">{{ error }}</p>
      <UButton @click="loadData" color="error" class="mt-4">重新載入</UButton>
    </div>

    <!-- Stats Dashboard -->
    <div v-else class="space-y-8">
      <!-- Achievement Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 shadow-lg">
          <div class="text-4xl mb-2">📚</div>
          <div class="text-3xl font-bold">{{ achievements?.total_words_practiced || 0 }}</div>
          <div class="text-blue-100">練習過的詞語</div>
        </div>

        <div class="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 shadow-lg">
          <div class="text-4xl mb-2">✅</div>
          <div class="text-3xl font-bold">{{ achievements?.overall_accuracy?.toFixed(1) || 0 }}%</div>
          <div class="text-green-100">整體準確率</div>
        </div>

        <div class="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 shadow-lg">
          <div class="text-4xl mb-2">⏱️</div>
          <div class="text-3xl font-bold">{{ achievements?.total_time_minutes?.toFixed(0) || 0 }}</div>
          <div class="text-purple-100">學習分鐘</div>
        </div>

        <div class="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-lg p-6 shadow-lg">
          <div class="text-4xl mb-2">🔥</div>
          <div class="text-3xl font-bold">{{ achievements?.streak_days || 0 }}</div>
          <div class="text-amber-100">連續學習天數</div>
        </div>
      </div>

      <!-- Weakest Words -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">❌ 最需要加強的詞語</h2>
        <div v-if="weakWords.length === 0" class="text-center py-8 text-gray-400">
          還未有數據
        </div>
        <div v-else class="space-y-3">
          <div 
            v-for="(word, index) in weakWords" 
            :key="word.id"
            class="flex items-center justify-between p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
          >
            <div class="flex items-center gap-4">
              <div class="text-2xl font-bold text-red-600">#{{ index + 1 }}</div>
              <div>
                <div class="text-xl font-bold">{{ word.chinese }} ({{ word.english }})</div>
                <div class="text-sm text-gray-600">
                  {{ word.total_attempts }} 次練習 · 
                  {{ word.correct_count }} 次答對
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-red-600">{{ word.accuracy_percent?.toFixed(0) }}%</div>
              <div class="text-xs text-gray-500">準確率</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Time Chart -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">📈 學習時間趨勢 (過去7日)</h2>
        <div v-if="learningTimeStats.length === 0" class="text-center py-8 text-gray-400">
          還未有數據
        </div>
        <div v-else class="space-y-2">
          <div 
            v-for="stat in learningTimeStats" 
            :key="stat.date"
            class="flex items-center gap-4"
          >
            <div class="w-24 text-sm text-gray-600">{{ formatDate(stat.date) }}</div>
            <div class="flex-1">
              <div class="bg-gray-200 rounded-full h-8 relative overflow-hidden">
                <div 
                  class="bg-gradient-to-r from-amber-500 to-amber-600 h-full flex items-center px-3 text-white font-bold text-sm"
                  :style="{ width: `${Math.min(100, (stat.accuracy_percent || 0))}%` }"
                >
                  {{ stat.accuracy_percent?.toFixed(0) }}%
                </div>
              </div>
            </div>
            <div class="w-32 text-right">
              <div class="font-bold">{{ stat.total_attempts }} 題</div>
              <div class="text-xs text-gray-500">{{ stat.total_time_minutes?.toFixed(1) }} 分鐘</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Game Mode Comparison -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">🎮 遊戲模式比較</h2>
        <div v-if="gameModeStats.length === 0" class="text-center py-8 text-gray-400">
          還未有數據
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div 
            v-for="mode in gameModeStats" 
            :key="mode.game_type"
            class="border-2 border-gray-200 rounded-lg p-4 hover:border-amber-500 transition-colors"
          >
            <div class="text-3xl mb-2">{{ getGameIcon(mode.game_type) }}</div>
            <div class="text-xl font-bold capitalize">{{ mode.game_type }}</div>
            <div class="mt-3 space-y-1">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">練習次數</span>
                <span class="font-bold">{{ mode.total_attempts }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">準確率</span>
                <span class="font-bold text-green-600">{{ mode.accuracy_percent?.toFixed(1) }}%</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">平均時間</span>
                <span class="font-bold">{{ (mode.avg_time_ms / 1000).toFixed(1) }}s</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Stats -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">📂 分類進度</h2>
        <div v-if="categoryStats.length === 0" class="text-center py-8 text-gray-400">
          還未有數據
        </div>
        <div v-else class="space-y-4">
          <div 
            v-for="category in categoryStats" 
            :key="category.category"
            class="border border-gray-200 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="text-xl font-bold capitalize">{{ category.category }}</div>
              <div class="text-sm text-gray-600">
                {{ category.words_practiced }} / {{ category.total_words }} 已練習
              </div>
            </div>
            <div class="bg-gray-200 rounded-full h-4 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-blue-500 to-purple-500 h-full"
                :style="{ width: `${(category.words_practiced / category.total_words * 100) || 0}%` }"
              ></div>
            </div>
            <div class="mt-2 flex justify-between text-sm text-gray-600">
              <span>已掌握: {{ category.words_mastered }}</span>
              <span>平均準確率: {{ category.avg_accuracy?.toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">⏰ 最近學習活動</h2>
        <div v-if="recentActivity.length === 0" class="text-center py-8 text-gray-400">
          還未有數據
        </div>
        <div v-else class="space-y-2">
          <div 
            v-for="activity in recentActivity" 
            :key="activity.id"
            class="flex items-center justify-between p-3 border-l-4 hover:bg-gray-50 transition-colors"
            :class="activity.correct ? 'border-green-500' : 'border-red-500'"
          >
            <div class="flex items-center gap-3">
              <div class="text-2xl">{{ activity.correct ? '✅' : '❌' }}</div>
              <div>
                <div class="font-bold">{{ activity.chinese }} ({{ activity.english }})</div>
                <div class="text-sm text-gray-500">
                  {{ activity.game_type }} · {{ formatDateTime(activity.created_at) }}
                </div>
              </div>
            </div>
            <div class="text-sm text-gray-600">
              {{ (activity.time_spent_ms / 1000).toFixed(1) }}s
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Use API composable
const { 
  getAchievementProgress,
  getWeakestWords,
  getLearningTimeStats,
  getGameModeStats,
  getCategoryStats,
  getRecentActivity,
  loading,
  error 
} = useAPI()

// Reactive data
const achievements = ref(null)
const weakWords = ref([])
const learningTimeStats = ref([])
const gameModeStats = ref([])
const categoryStats = ref([])
const recentActivity = ref([])

// Load all data
const loadData = async () => {
  try {
    // Load all stats in parallel
    const [
      achievementsData,
      weakWordsData,
      timeStatsData,
      gameModeData,
      categoryData,
      activityData
    ] = await Promise.all([
      getAchievementProgress(),
      getWeakestWords(5, 2),
      getLearningTimeStats(7),
      getGameModeStats(),
      getCategoryStats(),
      getRecentActivity(10)
    ])

    achievements.value = achievementsData
    weakWords.value = weakWordsData
    learningTimeStats.value = timeStatsData
    gameModeStats.value = gameModeData
    categoryStats.value = categoryData
    recentActivity.value = activityData
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

// Format date helper
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day}`
}

// Format datetime helper
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return '剛剛'
  if (diffMins < 60) return `${diffMins} 分鐘前`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} 小時前`
  
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays} 日前`
}

// Game icon helper
const getGameIcon = (gameType) => {
  const icons = {
    'flashcard': '🃏',
    'spelling': '🔤',
    'sentence': '📝'
  }
  return icons[gameType] || '🎮'
}

// Load data on mount
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* Smooth animations */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

.transition-colors {
  transition: background-color 0.2s, border-color 0.2s;
}
</style>
