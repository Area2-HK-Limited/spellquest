<template>
  <UContainer>
    <div class="py-8">
      <!-- Header -->
      <UPageHeader
        title="🎮 SpellQuest"
        description="默書小勇士 - 選擇一個遊戲開始溫習！"
        class="mb-12"
      />

      <!-- Game Cards Grid -->
      <ULandingGrid>
        <!-- Spelling Game -->
        <ULandingCard
          to="/spelling"
          title="英文串字"
          description="睇中文，串英文"
          icon="i-heroicons-language"
          color="primary"
        >
          <template #icon>
            <div class="text-6xl">🔤</div>
          </template>
        </ULandingCard>

        <!-- Sentence Game -->
        <ULandingCard
          to="/sentence"
          title="句子重組"
          description="排列正確句子順序"
          icon="i-heroicons-document-text"
          color="green"
        >
          <template #icon>
            <div class="text-6xl">📝</div>
          </template>
        </ULandingCard>

        <!-- Flashcard Game -->
        <ULandingCard
          to="/flashcard"
          title="中文認字"
          description="翻卡記憶遊戲"
          icon="i-heroicons-academic-cap"
          color="amber"
        >
          <template #icon>
            <div class="text-6xl">✏️</div>
          </template>
        </ULandingCard>

        <!-- Matching Game -->
        <ULandingCard
          to="/matching"
          title="配對遊戲"
          description="中英配對記憶"
          icon="i-heroicons-puzzle-piece"
          color="teal"
        >
          <template #icon>
            <div class="text-6xl">🔗</div>
          </template>
        </ULandingCard>

        <!-- Word Input -->
        <ULandingCard
          to="/input"
          title="輸入詞語"
          description="新增溫習內容"
          icon="i-heroicons-camera"
          color="purple"
        >
          <template #icon>
            <div class="text-6xl">📷</div>
          </template>
        </ULandingCard>

        <!-- Word List -->
        <ULandingCard
          to="/words"
          title="詞語列表"
          description="查看所有詞語"
          icon="i-heroicons-book-open"
          color="cyan"
        >
          <template #icon>
            <div class="text-6xl">📚</div>
          </template>
        </ULandingCard>

        <!-- Dictation -->
        <ULandingCard
          to="/dictation"
          title="聽寫模式"
          description="聽發音，寫答案"
          icon="i-heroicons-speaker-wave"
          color="pink"
        >
          <template #icon>
            <div class="text-6xl">🎯</div>
          </template>
        </ULandingCard>

        <!-- Stats -->
        <ULandingCard
          to="/stats"
          title="學習進度"
          description="睇下學咗幾多"
          icon="i-heroicons-chart-bar"
          color="rose"
        >
          <template #icon>
            <div class="text-6xl">📊</div>
          </template>
        </ULandingCard>
      </ULandingGrid>

      <!-- Footer -->
      <div class="text-center mt-12">
        <UAlert
          color="primary"
          variant="subtle"
          title="Made with ❤️ for 沛晨"
          icon="i-heroicons-heart"
        />
      </div>
    </div>
  </UContainer>
</template>

<script setup>
// Home page - clean and simple with Nuxt UI Pro
</script>
