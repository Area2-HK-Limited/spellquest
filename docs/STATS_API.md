# SpellQuest Stats API - 學習數據統計

學習數據統計 API endpoints，用於 dashboard 同進度追蹤。

## 📊 統計 Functions

### 1. 最弱詞語排名

獲取錯誤率最高嘅詞語，幫小朋友識別需要加強嘅地方。

```bash
POST /rpc/get_weakest_words
Content-Type: application/json

{
  "p_limit": 10,
  "p_min_attempts": 3
}

# Response
[
  {
    "id": 5,
    "chinese": "妹妹",
    "english": "younger sister",
    "category": "family",
    "total_attempts": 5,
    "correct_count": 1,
    "accuracy_percent": 20.00,
    "avg_time_ms": 8500.5
  },
  ...
]
```

**參數：**
- `p_limit` (optional): 返回幾多個詞語（default: 10）
- `p_min_attempts` (optional): 最少要練習幾多次先計算（default: 3）

---

### 2. 學習時間統計

按日期統計學習時間同準確率。

```bash
POST /rpc/get_learning_time_stats
Content-Type: application/json

{
  "p_days": 7
}

# Response
[
  {
    "date": "2026-01-30",
    "total_attempts": 25,
    "correct_count": 20,
    "accuracy_percent": 80.00,
    "total_time_minutes": 15.50,
    "avg_time_per_word_ms": 3720.0
  },
  {
    "date": "2026-01-29",
    "total_attempts": 18,
    "correct_count": 15,
    "accuracy_percent": 83.33,
    "total_time_minutes": 12.30,
    "avg_time_per_word_ms": 4100.0
  },
  ...
]
```

**參數：**
- `p_days` (optional): 過去幾多日（default: 7）

---

### 3. 遊戲模式統計

比較不同遊戲模式嘅表現。

```bash
POST /rpc/get_game_mode_stats

# Response
[
  {
    "game_type": "spelling",
    "total_attempts": 50,
    "correct_count": 40,
    "accuracy_percent": 80.00,
    "avg_time_ms": 4500.0,
    "last_played_at": "2026-01-30T09:00:00Z"
  },
  {
    "game_type": "flashcard",
    "total_attempts": 30,
    "correct_count": 25,
    "accuracy_percent": 83.33,
    "avg_time_ms": 3200.0,
    "last_played_at": "2026-01-30T08:30:00Z"
  },
  ...
]
```

---

### 4. 詞語分類統計

按分類（fruit, school, family 等）統計學習進度。

```bash
POST /rpc/get_category_stats

# Response
[
  {
    "category": "fruit",
    "total_words": 10,
    "practiced_words": 8,
    "mastered_words": 5,
    "avg_accuracy": 78.50
  },
  {
    "category": "school",
    "total_words": 15,
    "practiced_words": 10,
    "mastered_words": 6,
    "avg_accuracy": 72.30
  },
  ...
]
```

**定義：**
- `practiced_words`: 至少練習過 1 次
- `mastered_words`: 準確率 ≥80% 且練習 ≥3 次

---

### 5. 成就進度統計

總覽學習成就，用於 dashboard。

```bash
POST /rpc/get_achievement_progress

# Response
{
  "total_words_practiced": 25,
  "total_attempts": 150,
  "total_correct": 120,
  "overall_accuracy": 80.00,
  "total_time_hours": 2.50,
  "streak_days": 5,
  "mastered_words": 12
}
```

**指標說明：**
- `total_words_practiced`: 總共練習過幾多個詞語
- `total_attempts`: 總練習次數
- `total_correct`: 答對次數
- `overall_accuracy`: 整體準確率
- `total_time_hours`: 累計學習時間（小時）
- `streak_days`: 連續學習天數
- `mastered_words`: 已掌握詞語數量（≥80% accuracy, ≥3 attempts）

---

### 6. 最近學習記錄

顯示最近嘅學習活動，用於 timeline。

```bash
POST /rpc/get_recent_learning_activity
Content-Type: application/json

{
  "p_limit": 10
}

# Response
[
  {
    "id": 123,
    "word_id": 5,
    "chinese": "蘋果",
    "english": "apple",
    "game_type": "spelling",
    "correct": true,
    "time_spent_ms": 4500,
    "created_at": "2026-01-30T09:15:00Z"
  },
  ...
]
```

---

## 📈 Dashboard 整合範例

### Nuxt Composable

```typescript
// composables/useStats.ts
export const useStats = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'http://localhost:3001'

  // Get weakest words
  const getWeakestWords = async (limit = 5) => {
    return await $fetch(`${apiUrl}/rpc/get_weakest_words`, {
      method: 'POST',
      body: { p_limit: limit, p_min_attempts: 3 }
    })
  }

  // Get learning time stats
  const getLearningTimeStats = async (days = 7) => {
    return await $fetch(`${apiUrl}/rpc/get_learning_time_stats`, {
      method: 'POST',
      body: { p_days: days }
    })
  }

  // Get achievement progress
  const getAchievementProgress = async () => {
    const response = await $fetch(`${apiUrl}/rpc/get_achievement_progress`, {
      method: 'POST'
    })
    return response
  }

  // Get game mode stats
  const getGameModeStats = async () => {
    return await $fetch(`${apiUrl}/rpc/get_game_mode_stats`, {
      method: 'POST'
    })
  }

  // Get category stats
  const getCategoryStats = async () => {
    return await $fetch(`${apiUrl}/rpc/get_category_stats`, {
      method: 'POST'
    })
  }

  // Get recent activity
  const getRecentActivity = async (limit = 10) => {
    return await $fetch(`${apiUrl}/rpc/get_recent_learning_activity`, {
      method: 'POST',
      body: { p_limit: limit }
    })
  }

  return {
    getWeakestWords,
    getLearningTimeStats,
    getAchievementProgress,
    getGameModeStats,
    getCategoryStats,
    getRecentActivity
  }
}
```

### Dashboard 使用範例

```vue
<script setup>
const { 
  getAchievementProgress, 
  getWeakestWords,
  getLearningTimeStats 
} = useStats()

// Load dashboard data
const achievements = ref({})
const weakWords = ref([])
const timeStats = ref([])

onMounted(async () => {
  achievements.value = await getAchievementProgress()
  weakWords.value = await getWeakestWords(5)
  timeStats.value = await getLearningTimeStats(7)
})
</script>

<template>
  <div class="dashboard">
    <!-- Achievement Cards -->
    <div class="stats-cards">
      <Card>
        <h3>總練習詞語</h3>
        <p class="big-number">{{ achievements.total_words_practiced }}</p>
      </Card>
      
      <Card>
        <h3>整體準確率</h3>
        <p class="big-number">{{ achievements.overall_accuracy }}%</p>
      </Card>
      
      <Card>
        <h3>連續學習</h3>
        <p class="big-number">{{ achievements.streak_days }} 天</p>
      </Card>
    </div>

    <!-- Weakest Words -->
    <Card>
      <h3>需要加強嘅詞語</h3>
      <ul>
        <li v-for="word in weakWords" :key="word.id">
          {{ word.chinese }} ({{ word.english }}) - 
          準確率: {{ word.accuracy_percent }}%
        </li>
      </ul>
    </Card>

    <!-- Learning Time Chart -->
    <Card>
      <h3>過去 7 日學習時間</h3>
      <BarChart :data="timeStats" />
    </Card>
  </div>
</template>
```

---

## 🎯 使用場景

### 家長 Dashboard
- 顯示小朋友嘅整體進度
- 識別需要加強嘅詞語
- 追蹤每日學習時間

### 小朋友進度頁面
- 顯示已掌握嘅詞語
- 展示成就徽章
- 鼓勵連續學習

### 老師報告
- 比較不同遊戲模式嘅效果
- 按分類分析學習情況
- 匯出學習報告

---

## 📊 Performance Tips

- 統計 functions 會計算大量數據，建議加 cache
- `get_achievement_progress` 返回 JSON，可以直接用於前端
- 使用 `p_min_attempts` 過濾練習次數少嘅詞語，提高準確性

---

## 🔄 Migration

如果 database 已經 running：

```bash
./scripts/apply-functions.sh
```

會自動 apply `stats-functions.sql`。
