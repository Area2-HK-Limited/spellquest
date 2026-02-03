<template>
  <UContainer>
    <div class="py-8">
      <!-- Header -->
      <UPageHeader
        title="📚 詞語列表"
        description="所有詞語一覽"
      >
        <template #links>
          <UButton to="/" variant="ghost" icon="i-heroicons-arrow-left">返回</UButton>
          <UButton to="/input" color="primary" icon="i-heroicons-plus">新增</UButton>
        </template>
      </UPageHeader>

      <!-- Filter -->
      <UCard class="mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <UInput 
            v-model="searchQuery" 
            placeholder="搜尋詞語..." 
            icon="i-heroicons-magnifying-glass"
            class="flex-1"
          />
          <USelect v-model="filterCategory" :options="categoryOptions" placeholder="分類" />
        </div>
      </UCard>

      <!-- Loading State -->
      <UCard v-if="pending">
        <div class="space-y-4">
          <USkeleton class="h-12 w-full" />
          <USkeleton class="h-12 w-full" />
          <USkeleton class="h-12 w-full" />
        </div>
      </UCard>

      <!-- Error State -->
      <UCard v-else-if="error">
        <UAlert 
          color="red" 
          title="載入失敗" 
          :description="error.message"
        />
      </UCard>

      <!-- Word List -->
      <UCard v-else>
        <UTable 
          :rows="filteredWords" 
          :columns="columns"
          :loading="pending"
        >
          <template #chinese-data="{ row }">
            <span class="text-xl font-bold text-cyan-600">{{ row.chinese || '-' }}</span>
          </template>
          
          <template #english-data="{ row }">
          <span class="text-gray-700">{{ row.english }}</span>
        </template>
        
        <template #category-data="{ row }">
          <UBadge :color="getCategoryColor(row.category)">{{ row.category || 'custom' }}</UBadge>
        </template>
        
        <template #actions-data="{ row }">
          <div class="flex gap-2">
            <UButton 
              @click="speak(row.chinese || row.english)" 
              color="primary" 
              variant="ghost" 
              size="sm"
              icon="i-heroicons-speaker-wave"
            />
            <UButton 
              @click="openEditModal(row)" 
              color="blue" 
              variant="ghost" 
              size="sm"
              icon="i-heroicons-pencil-square"
            />
            <UButton 
              @click="confirmDelete(row)" 
              color="red" 
              variant="ghost" 
              size="sm"
              icon="i-heroicons-trash"
            />
          </div>
        </template>
      </UTable>
      
      <template #footer v-if="filteredWords.length === 0">
        <div class="text-center text-gray-500">
          冇搵到詞語
        </div>
      </template>
      </UCard>

      <!-- Stats -->
      <UAlert 
        v-if="filteredWords.length > 0"
        color="primary" 
        variant="subtle"
        class="mt-6"
      >
        <template #title>
          <div class="text-center">共 {{ filteredWords.length }} 個詞語</div>
        </template>
      </UAlert>

    <!-- Edit Modal -->
    <UModal v-model="isEditModalOpen" title="編輯詞語">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">{{ editingWord?.id ? '編輯詞語' : '新增詞語' }}</h3>
        </template>
        
        <UForm :state="editingWord" class="space-y-4">
          <UFormGroup label="英文" name="english" required>
            <UInput v-model="editingWord.english" placeholder="例如：apple" />
          </UFormGroup>
          
          <UFormGroup label="中文" name="chinese">
            <UInput v-model="editingWord.chinese" placeholder="例如：蘋果" />
          </UFormGroup>
          
          <UFormGroup label="分類" name="category">
            <USelect v-model="editingWord.category" :options="categoryOptions" />
          </UFormGroup>
        </UForm>
        
        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="ghost" @click="isEditModalOpen = false">取消</UButton>
            <UButton color="primary" @click="saveWord" :loading="isSaving">儲存</UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- Delete Confirmation Modal -->
    <UModal v-model="isDeleteModalOpen" title="確認刪除">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-red-600">⚠️ 確認刪除</h3>
        </template>
        
        <p class="text-gray-700">
          確定要刪除詞語「<span class="font-bold">{{ deletingWord?.english }}</span>」嗎？
        </p>
        <p class="text-sm text-gray-500 mt-2">
          此操作無法復原。
        </p>
        
        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="ghost" @click="isDeleteModalOpen = false">取消</UButton>
            <UButton color="red" @click="deleteWord" :loading="isDeleting">刪除</UButton>
          </div>
        </template>
      </UCard>
    </UModal>
    </div>
  </UContainer>
</template>

<script setup>
import { ref, computed } from 'vue'

// Fetch words from PostgREST API
const { data: words, pending, error, refresh } = await useFetch('http://192.168.139.142:3001/words', {
  default: () => []
})

const searchQuery = ref('')
const filterCategory = ref('')

// Table columns (removed pinyin column)
const columns = [
  { id: 'english', key: 'english', label: '英文', sortable: true },
  { id: 'chinese', key: 'chinese', label: '中文' },
  { id: 'category', key: 'category', label: '分類' },
  { id: 'actions', key: 'actions', label: '操作' }
]

const categoryOptions = [
  { label: '全部', value: '' },
  { label: '水果', value: 'fruit' },
  { label: '學校', value: 'school' },
  { label: '家庭', value: 'family' },
  { label: '自然', value: 'nature' },
  { label: '自訂', value: 'custom' }
]

const filteredWords = computed(() => {
  if (!words.value) return []
  
  return words.value.filter(word => {
    const matchesSearch = !searchQuery.value || 
      (word.chinese && word.chinese.includes(searchQuery.value)) ||
      word.english.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesCategory = !filterCategory.value || word.category === filterCategory.value
    
    return matchesSearch && matchesCategory
  })
})

const getCategoryColor = (category) => {
  const colors = {
    fruit: 'green',
    school: 'blue',
    family: 'purple',
    nature: 'teal',
    custom: 'gray'
  }
  return colors[category] || 'gray'
}

const speak = (text) => {
  if (!text) return
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'zh-HK'
  speechSynthesis.speak(utterance)
}

// Edit Modal
const isEditModalOpen = ref(false)
const editingWord = ref({})
const isSaving = ref(false)

const openEditModal = (word) => {
  editingWord.value = { ...word }
  isEditModalOpen.value = true
}

const saveWord = async () => {
  isSaving.value = true
  
  try {
    if (editingWord.value.id) {
      // Update existing word
      await $fetch(`http://192.168.139.142:3001/words?id=eq.${editingWord.value.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation' },
        body: JSON.stringify({
          english: editingWord.value.english,
          chinese: editingWord.value.chinese || '',
          category: editingWord.value.category || 'custom'
        })
      })
    } else {
      // Create new word
      await $fetch('http://192.168.139.142:3001/words', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation' },
        body: JSON.stringify({
          english: editingWord.value.english,
          chinese: editingWord.value.chinese || '',
          category: editingWord.value.category || 'custom',
          pinyin: '' // Empty pinyin as per requirement
        })
      })
    }
    
    // Refresh data
    await refresh()
    isEditModalOpen.value = false
  } catch (error) {
    console.error('Failed to save word:', error)
    alert('儲存失敗：' + error.message)
  } finally {
    isSaving.value = false
  }
}

// Delete Modal
const isDeleteModalOpen = ref(false)
const deletingWord = ref(null)
const isDeleting = ref(false)

const confirmDelete = (word) => {
  deletingWord.value = word
  isDeleteModalOpen.value = true
}

const deleteWord = async () => {
  isDeleting.value = true
  
  try {
    await $fetch(`http://192.168.139.142:3001/words?id=eq.${deletingWord.value.id}`, {
      method: 'DELETE'
    })
    
    // Refresh data
    await refresh()
    isDeleteModalOpen.value = false
  } catch (error) {
    console.error('Failed to delete word:', error)
    alert('刪除失敗：' + error.message)
  } finally {
    isDeleting.value = false
  }
}
</script>
