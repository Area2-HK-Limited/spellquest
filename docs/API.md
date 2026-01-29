# SpellQuest Backend API 文檔

SpellQuest 後端 API 整合指南，包括 PostgREST 同 OCR Service。

## 📡 服務列表

| Service | Port | URL | 用途 |
|---------|------|-----|------|
| PostgreSQL | 5432 | `localhost:5432` | 資料庫 |
| PostgREST | 3001 | `http://localhost:3001` | RESTful API |
| OCR Service | 3002 | `http://localhost:3002` | OCR 識別 |
| Frontend | 3000 | `http://localhost:3000` | Nuxt App |
| Adminer | 8080 | `http://localhost:8080` | DB Admin |

---

## 1️⃣ PostgREST API (Port 3001)

### 基本 CRUD

PostgREST 自動生成所有 table 嘅 RESTful endpoints：

```bash
# Get all words
GET /words

# Get words with filter
GET /words?category=eq.fruit&grade=eq.P1

# Get single word
GET /words?id=eq.1

# Create word
POST /words
Content-Type: application/json

{
  "chinese": "蘋果",
  "english": "apple",
  "pinyin": "píng guǒ",
  "category": "fruit",
  "grade": "P1"
}

# Update word
PATCH /words?id=eq.1
Content-Type: application/json

{
  "english": "red apple"
}

# Delete word
DELETE /words?id=eq.1
```

### Custom Functions (RPC)

呢啲係我哋自訂嘅 PostgreSQL functions，可以用 RPC 方式 call：

#### 1. 隨機抽詞語

```bash
POST /rpc/get_random_words
Content-Type: application/json

{
  "p_category": "fruit",
  "p_grade": "P1",
  "p_limit": 10
}

# Response
[
  {
    "id": 1,
    "chinese": "蘋果",
    "english": "apple",
    "pinyin": "píng guǒ",
    "category": "fruit",
    "grade": "P1"
  },
  ...
]
```

#### 2. 根據詞語集生成題目

```bash
POST /rpc/get_quiz_questions
Content-Type: application/json

{
  "p_word_set_id": 1
}

# Response
[
  {
    "id": 1,
    "chinese": "蘋果",
    "english": "apple",
    "pinyin": "píng guǒ",
    "category": "fruit"
  },
  ...
]
```

#### 3. 提交學習記錄

```bash
POST /rpc/submit_learning_record
Content-Type: application/json

{
  "p_word_id": 1,
  "p_game_type": "spelling",
  "p_correct": true,
  "p_time_spent_ms": 5000
}

# Response
123  # record_id
```

Valid `game_type`: `spelling`, `sentence`, `flashcard`

#### 4. 隨機抽句子

```bash
POST /rpc/get_random_sentences
Content-Type: application/json

{
  "p_category": "school",
  "p_grade": "P1",
  "p_limit": 5
}

# Response
[
  {
    "id": 1,
    "content": "I go to school.",
    "translation": "我去上學。",
    "category": "school"
  },
  ...
]
```

#### 5. 獲取詞語集詳情

```bash
POST /rpc/get_word_set_details
Content-Type: application/json

{
  "p_word_set_id": 1
}

# Response
[
  {
    "word_set_id": 1,
    "word_set_name": "第22週中文默書",
    "word_set_description": "1月28日默書範圍",
    "word_id": 1,
    "chinese": "蘋果",
    "english": "apple",
    "pinyin": "píng guǒ",
    "order_num": 1
  },
  ...
]
```

#### 6. 批量插入詞語 (for OCR)

```bash
POST /rpc/bulk_insert_words
Content-Type: application/json

{
  "p_words": [
    {
      "chinese": "蘋果",
      "english": "apple",
      "pinyin": "píng guǒ",
      "category": "fruit",
      "grade": "P1"
    },
    {
      "chinese": "香蕉",
      "english": "banana",
      "pinyin": "xiāng jiāo",
      "category": "fruit",
      "grade": "P1"
    }
  ]
}

# Response
2  # number of words inserted
```

### Views (統計數據)

#### 詞語準確率統計

```bash
GET /word_accuracy_stats?total_attempts=gt.0

# Response
[
  {
    "id": 1,
    "chinese": "蘋果",
    "english": "apple",
    "category": "fruit",
    "total_attempts": 10,
    "correct_count": 8,
    "accuracy_percent": 80.00,
    "avg_time_ms": 4500.5
  },
  ...
]
```

#### 學習進度

```bash
GET /learning_progress?order=date.desc

# Response
[
  {
    "game_type": "spelling",
    "date": "2026-01-30",
    "total_attempts": 20,
    "correct_count": 15,
    "accuracy_percent": 75.00
  },
  ...
]
```

---

## 2️⃣ OCR Service (Port 3002)

### Health Check

```bash
GET /health

# Response
{
  "status": "healthy",
  "tesseract_version": "5.x.x"
}
```

### 基本 OCR

```bash
POST /ocr/upload
Content-Type: multipart/form-data

# Body: file (image)

# Response
{
  "text": "蘋果 apple píng guǒ\n香蕉 banana xiāng jiāo",
  "words": ["蘋果", "apple", "香蕉", "banana", ...],
  "lines": ["蘋果 apple píng guǒ", "香蕉 banana xiāng jiāo"],
  "image_size": [1920, 1080]
}
```

### 智能詞語提取

```bash
POST /ocr/extract-vocab
Content-Type: multipart/form-data

# Body: file (image)

# Response
{
  "vocabulary": [
    {
      "chinese": "蘋果",
      "english": "apple",
      "pinyin": "píng guǒ"
    },
    {
      "chinese": "香蕉",
      "english": "banana",
      "pinyin": "xiāng jiāo"
    }
  ],
  "raw_text": "原始OCR文字"
}
```

---

## 📝 Frontend 整合範例

### Nuxt 3 Composable

```typescript
// composables/useAPI.ts
export const useAPI = () => {
  const config = useRuntimeConfig()
  const postgrestURL = config.public.apiUrl || 'http://localhost:3001'
  const ocrURL = 'http://localhost:3002'

  // Get random words for spelling game
  const getRandomWords = async (category: string = 'fruit', limit: number = 10) => {
    const response = await $fetch(`${postgrestURL}/rpc/get_random_words`, {
      method: 'POST',
      body: {
        p_category: category,
        p_grade: 'P1',
        p_limit: limit
      }
    })
    return response
  }

  // Submit learning record
  const submitRecord = async (wordId: number, gameType: string, correct: boolean, timeMs: number) => {
    const response = await $fetch(`${postgrestURL}/rpc/submit_learning_record`, {
      method: 'POST',
      body: {
        p_word_id: wordId,
        p_game_type: gameType,
        p_correct: correct,
        p_time_spent_ms: timeMs
      }
    })
    return response
  }

  // OCR upload
  const ocrUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await $fetch(`${ocrURL}/ocr/extract-vocab`, {
      method: 'POST',
      body: formData
    })
    return response
  }

  // Get learning progress
  const getLearningProgress = async () => {
    const response = await $fetch(`${postgrestURL}/learning_progress?order=date.desc`)
    return response
  }

  return {
    getRandomWords,
    submitRecord,
    ocrUpload,
    getLearningProgress
  }
}
```

### 使用範例

```vue
<script setup>
const { getRandomWords, submitRecord } = useAPI()

// Load random words for game
const words = ref([])
onMounted(async () => {
  words.value = await getRandomWords('fruit', 10)
})

// Submit result
const handleAnswer = async (wordId, correct, timeMs) => {
  await submitRecord(wordId, 'spelling', correct, timeMs)
}
</script>
```

---

## 🔒 安全性

- PostgREST 使用 `web_anon` role，已設定好權限
- OCR Service 只接受 image/* content type
- 所有 custom functions 使用 `SECURITY DEFINER`

---

## 🧪 測試

```bash
# Start all services
docker-compose up -d

# Check services
curl http://localhost:3001/words
curl http://localhost:3002/health

# Test OCR
curl -X POST http://localhost:3002/ocr/upload \
  -F "file=@test.jpg"
```

---

## 📊 Performance Tips

- PostgREST 支援 query parameters for filtering, sorting, pagination
- 使用 `select=` 只 fetch 需要嘅 columns
- 使用 `limit=` 做 pagination

範例：

```bash
# Only get id, chinese, english
GET /words?select=id,chinese,english

# Pagination
GET /words?limit=10&offset=0

# Sorting
GET /words?order=created_at.desc

# Multiple filters
GET /words?category=eq.fruit&grade=eq.P1&order=chinese.asc
```

---

完整 API docs: http://localhost:3001/
