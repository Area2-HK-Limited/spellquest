<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

// Sidebar state
const open = ref(false)

// Navigation links for sidebar
const links: NavigationMenuItem[][] = [[
  {
    label: '首頁',
    icon: 'i-heroicons-home',
    to: '/',
    onSelect: () => { open.value = false }
  },
  {
    label: '📷 輸入詞語',
    icon: 'i-heroicons-camera',
    to: '/input',
    onSelect: () => { open.value = false }
  },
  {
    label: '📚 詞語列表',
    icon: 'i-heroicons-book-open',
    to: '/words',
    onSelect: () => { open.value = false }
  }
], [
  {
    label: '遊戲',
    icon: 'i-heroicons-puzzle-piece',
    type: 'trigger',
    defaultOpen: true,
    children: [
      {
        label: '🔤 英文串字',
        to: '/spelling',
        onSelect: () => { open.value = false }
      },
      {
        label: '📝 句子重組',
        to: '/sentence',
        onSelect: () => { open.value = false }
      },
      {
        label: '✏️ 中文認字',
        to: '/flashcard',
        onSelect: () => { open.value = false }
      },
      {
        label: '🔗 配對遊戲',
        to: '/matching',
        onSelect: () => { open.value = false }
      },
      {
        label: '🎯 聽寫模式',
        to: '/dictation',
        onSelect: () => { open.value = false }
      }
    ]
  }
]]
</script>

<template>
  <UDashboardGroup>
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      class="bg-elevated/25"
    >
      <template #header="{ collapsed }">
        <div class="flex items-center gap-2 p-2" :class="{ 'justify-center': collapsed }">
          <span class="text-2xl">🎮</span>
          <span v-if="!collapsed" class="font-bold text-lg">SpellQuest</span>
        </div>
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[0]"
          orientation="vertical"
          tooltip
        />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[1]"
          orientation="vertical"
          tooltip
          class="mt-4"
        />
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
