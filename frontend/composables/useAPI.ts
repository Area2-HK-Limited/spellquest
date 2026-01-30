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

  /**
   * Get weakest words (highest error rate)
   * @param limit Number of words to return
   * @param minAttempts Minimum attempts required
   */
  const getWeakestWords = async (
    limit: number = 10,
    minAttempts: number = 3
  ): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_weakest_words`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          p_limit: limit,
          p_min_attempts: minAttempts,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getWeakestWords error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Get learning time stats by date
   * @param days Number of days to look back
   */
  const getLearningTimeStats = async (days: number = 7): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_learning_time_stats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ p_days: days }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getLearningTimeStats error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Get game mode stats (comparison across different game types)
   */
  const getGameModeStats = async (): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_game_mode_stats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getGameModeStats error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Get category stats (words practiced/mastered by category)
   */
  const getCategoryStats = async (): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_category_stats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getCategoryStats error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Get achievement progress
   */
  const getAchievementProgress = async (): Promise<any> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_achievement_progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data[0] || null
    } catch (e: any) {
      error.value = e.message
      console.error('getAchievementProgress error:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Get recent learning activity
   * @param limit Number of recent records
   */
  const getRecentActivity = async (limit: number = 20): Promise<any[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/rpc/get_recent_learning_activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ p_limit: limit }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (e: any) {
      error.value = e.message
      console.error('getRecentActivity error:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    // Basic APIs
    getRandomWords,
    submitLearningRecord,
    getWordAccuracyStats,
    getLearningProgress,
    // Stats APIs
    getWeakestWords,
    getLearningTimeStats,
    getGameModeStats,
    getCategoryStats,
    getAchievementProgress,
    getRecentActivity,
  }
}
