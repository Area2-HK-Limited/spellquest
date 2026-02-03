<script setup lang="ts">
// Game cards data
const games = [
  {
    title: '🔤 英文串字',
    description: '睇中文，串英文',
    to: '/spelling'
  },
  {
    title: '📝 句子重組',
    description: '排列正確句子順序',
    to: '/sentence'
  },
  {
    title: '✏️ 中文認字',
    description: '翻卡記憶遊戲',
    to: '/flashcard'
  },
  {
    title: '🔗 配對遊戲',
    description: '中英配對記憶',
    to: '/matching'
  },
  {
    title: '🎯 聽寫模式',
    description: '聽發音，寫答案',
    to: '/dictation'
  }
]

const tools = [
  {
    title: '📷 輸入詞語',
    description: '拍照或手動新增詞語',
    to: '/input'
  },
  {
    title: '📚 詞語列表',
    description: '查看及管理所有詞語',
    to: '/words'
  }
]
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="🎮 SpellQuest 默書小勇士">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="p-6 space-y-8">
        <!-- Hero Section -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold mb-2">歡迎返嚟！👋</h1>
          <p class="text-gray-500">選擇一個遊戲開始溫習</p>
        </div>

        <!-- Games Section -->
        <div>
          <h2 class="text-xl font-semibold mb-4">🎮 遊戲模式</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <NuxtLink
              v-for="game in games"
              :key="game.to"
              :to="game.to"
              class="block"
            >
              <UCard class="hover:shadow-lg hover:ring-primary transition-all cursor-pointer h-full">
                <div class="text-center py-4">
                  <div class="text-4xl mb-3">{{ game.title.split(' ')[0] }}</div>
                  <h3 class="font-bold text-lg">{{ game.title.split(' ').slice(1).join(' ') }}</h3>
                  <p class="text-gray-500 text-sm mt-1">{{ game.description }}</p>
                </div>
              </UCard>
            </NuxtLink>
          </div>
        </div>

        <!-- Tools Section -->
        <div>
          <h2 class="text-xl font-semibold mb-4">🛠️ 工具</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <NuxtLink
              v-for="tool in tools"
              :key="tool.to"
              :to="tool.to"
              class="block"
            >
              <UCard class="hover:shadow-lg hover:ring-primary transition-all cursor-pointer h-full">
                <div class="text-center py-4">
                  <div class="text-4xl mb-3">{{ tool.title.split(' ')[0] }}</div>
                  <h3 class="font-bold text-lg">{{ tool.title.split(' ').slice(1).join(' ') }}</h3>
                  <p class="text-gray-500 text-sm mt-1">{{ tool.description }}</p>
                </div>
              </UCard>
            </NuxtLink>
          </div>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
