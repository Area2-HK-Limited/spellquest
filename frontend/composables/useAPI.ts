// composables/useAPI.ts
import { ref } from 'vue'

const API_BASE = 'http://localhost:3001'

interface Word {
  id: number
  chinese: string
  english: string
  pinyin?: string
  grade?: string
  category?: string
}

interface LearningRecord {
  word_id: number
  game_type: string
  correct: boolean
  time_spent_ms: number
}

export const useAPI = () => {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Get random words from database
   * @param category Optional category filter
   * @param grade Optional grade filter
   * @param limit Number of words to fetch (default: 10)
   */
  const getRandomWords = async (
    category?: string,
    grade?: string,
    limit: number = 10
  ): Promise<Word[]> => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (category) params.append('category', category)
      if (grade) params.append('grade', grade)
      params.append('limit', limit.toString())

      const response = await fetch(
        `${API_BASE}/rpc/get_random_words?${params.toString()}`
      )

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getRandomWords error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Submit learning record
   * @param record Learning record data
   */
  const submitLearningRecord = async (
    record: LearningRecord
  ): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/submit_learning_record`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(record),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      return true
    } catch (e: any) {
      error.value = e.message
      console.error('submitLearningRecord error:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Get word accuracy stats
   */
  const getWordAccuracyStats = async (): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/word_accuracy_stats`)

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getWordAccuracyStats error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Get learning progress
   */
  const getLearningProgress = async (): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/learning_progress`)

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getLearningProgress error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    getRandomWords,
    submitLearningRecord,
    getWordAccuracyStats,
    getLearningProgress,
  }
}
