<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="text-center mb-12">
      <h1 class="text-5xl font-bold text-indigo-600 mb-4">
        🎮 SpellQuest
      </h1>
      <p class="text-2xl text-gray-600">默書小勇士</p>
      <p class="text-lg text-gray-500 mt-2">選擇一個遊戲開始溫習！</p>
    </div>

    <!-- Game Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
      <!-- Spelling Game -->
      <NuxtLink to="/spelling" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-indigo-50">
        <div class="text-6xl mb-4">🔤</div>
        <h2 class="text-2xl font-bold text-indigo-600 mb-2">英文串字</h2>
        <p class="text-gray-600">睇中文，串英文</p>
        <div class="mt-4">
          <UBadge color="primary" size="lg">Spelling</UBadge>
        </div>
      </NuxtLink>

      <!-- Sentence Game -->
      <NuxtLink to="/sentence" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-green-50">
        <div class="text-6xl mb-4">📝</div>
        <h2 class="text-2xl font-bold text-green-600 mb-2">句子重組</h2>
        <p class="text-gray-600">排列正確句子順序</p>
        <div class="mt-4">
          <UBadge color="success" size="lg">Sentence</UBadge>
        </div>
      </NuxtLink>

      <!-- Flashcard Game -->
      <NuxtLink to="/flashcard" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-amber-50">
        <div class="text-6xl mb-4">✏️</div>
        <h2 class="text-2xl font-bold text-amber-600 mb-2">中文認字</h2>
        <p class="text-gray-600">翻卡記憶遊戲</p>
        <div class="mt-4">
          <UBadge color="warning" size="lg">Flashcard</UBadge>
        </div>
      </NuxtLink>

      <!-- Word Input -->
      <NuxtLink to="/input" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-purple-50">
        <div class="text-6xl mb-4">📷</div>
        <h2 class="text-2xl font-bold text-purple-600 mb-2">輸入詞語</h2>
        <p class="text-gray-600">新增溫習內容</p>
        <div class="mt-4">
          <UBadge color="violet" size="lg">Input</UBadge>
        </div>
      </NuxtLink>

      <!-- Word List -->
      <NuxtLink to="/words" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-cyan-50">
        <div class="text-6xl mb-4">📚</div>
        <h2 class="text-2xl font-bold text-cyan-600 mb-2">詞語列表</h2>
        <p class="text-gray-600">查看所有詞語</p>
        <div class="mt-4">
          <UBadge color="info" size="lg">Words</UBadge>
        </div>
      </NuxtLink>

      <!-- Stats -->
      <NuxtLink to="/stats" class="sq-card bg-white p-8 text-center cursor-pointer hover:bg-rose-50">
        <div class="text-6xl mb-4">📊</div>
        <h2 class="text-2xl font-bold text-rose-600 mb-2">學習進度</h2>
        <p class="text-gray-600">睇下學咗幾多</p>
        <div class="mt-4">
          <UBadge color="error" size="lg">Stats</UBadge>
        </div>
      </NuxtLink>
    </div>

    <!-- Footer -->
    <div class="text-center mt-12 text-gray-500">
      <p>Made with ❤️ for 沛晨</p>
    </div>
  </div>
</template>

<script setup>
// Home page - no special logic needed
</script>
