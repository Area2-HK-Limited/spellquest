<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="text-2xl">← 返回</NuxtLink>
      <div class="text-center">
        <h1 class="text-3xl font-bold text-rose-600">📊 學習進度</h1>
        <p class="text-gray-600">睇下你學咗幾多！</p>
      </div>
      <div></div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="sq-card bg-white p-6 text-center">
        <div class="text-4xl mb-2">📚</div>
        <div class="text-3xl font-bold text-indigo-600">{{ stats.totalWords }}</div>
        <div class="text-gray-500">總詞語</div>
      </div>
      
      <div class="sq-card bg-white p-6 text-center">
        <div class="text-4xl mb-2">✅</div>
        <div class="text-3xl font-bold text-green-600">{{ stats.correctAnswers }}</div>
        <div class="text-gray-500">答對次數</div>
      </div>
      
      <div class="sq-card bg-white p-6 text-center">
        <div class="text-4xl mb-2">🎮</div>
        <div class="text-3xl font-bold text-purple-600">{{ stats.gamesPlayed }}</div>
        <div class="text-gray-500">遊戲次數</div>
      </div>
      
      <div class="sq-card bg-white p-6 text-center">
        <div class="text-4xl mb-2">⭐</div>
        <div class="text-3xl font-bold text-amber-600">{{ stats.accuracy }}%</div>
        <div class="text-gray-500">正確率</div>
      </div>
    </div>

    <!-- Achievements -->
    <div class="sq-card bg-white p-6 mb-8">
      <h2 class="text-xl font-bold text-gray-700 mb-4">🏆 成就徽章</h2>
      
      <div class="grid grid-cols-3 md:grid-cols-6 gap-4">
        <div 
          v-for="achievement in achievements" 
          :key="achievement.id"
          class="text-center p-4 rounded-xl transition-all"
          :class="achievement.unlocked ? 'bg-amber-50' : 'bg-gray-100 opacity-50'"
        >
          <div class="text-4xl mb-2">{{ achievement.icon }}</div>
          <div class="text-sm font-medium" :class="achievement.unlocked ? 'text-amber-700' : 'text-gray-400'">
            {{ achievement.name }}
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="sq-card bg-white p-6">
      <h2 class="text-xl font-bold text-gray-700 mb-4">📅 最近活動</h2>
      
      <div class="space-y-3">
        <div 
          v-for="activity in recentActivity" 
          :key="activity.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <span class="text-2xl">{{ activity.icon }}</span>
            <div>
              <div class="font-medium text-gray-700">{{ activity.description }}</div>
              <div class="text-sm text-gray-500">{{ activity.time }}</div>
            </div>
          </div>
          <UBadge :color="activity.success ? 'success' : 'neutral'">
            {{ activity.success ? '+1 ⭐' : '再試' }}
          </UBadge>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref({
  totalWords: 16,
  correctAnswers: 42,
  gamesPlayed: 12,
  accuracy: 85
})

const achievements = ref([
  { id: 1, name: '初學者', icon: '🌱', unlocked: true },
  { id: 2, name: '勤力蜂', icon: '🐝', unlocked: true },
  { id: 3, name: '串字王', icon: '👑', unlocked: true },
  { id: 4, name: '記憶大師', icon: '🧠', unlocked: false },
  { id: 5, name: '完美答案', icon: '💯', unlocked: false },
  { id: 6, name: '堅持7日', icon: '🔥', unlocked: false }
])

const recentActivity = ref([
  { id: 1, icon: '🔤', description: '完成英文串字：apple', time: '剛剛', success: true },
  { id: 2, icon: '📝', description: '完成句子重組', time: '5分鐘前', success: true },
  { id: 3, icon: '✏️', description: '認字練習：蘋果', time: '10分鐘前', success: true },
  { id: 4, icon: '🔤', description: '英文串字：banana', time: '15分鐘前', success: false },
  { id: 5, icon: '✏️', description: '認字練習：香蕉', time: '20分鐘前', success: true }
])
</script>
