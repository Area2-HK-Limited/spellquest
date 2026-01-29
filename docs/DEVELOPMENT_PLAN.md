# SpellQuest 默書小勇士 - 開發計劃書

## 📋 項目概述

**項目名稱：** SpellQuest 默書小勇士  
**目標用戶：** 沛晨（7歲，小一學生）  
**開發日期：** 2026-01-30  
**開發者：** M01 (AI Assistant)

## 🎯 項目目標

為小一學生開發一個有趣嘅默書溫習平台，透過遊戲化方式提升學習興趣。

## 👤 用戶背景

- **姓名：** 唐沛晨
- **學校：** 中華基督教會基慧小學（馬灣）
- **班級：** 1C
- **默書日：**
  - 星期二：中文默書
  - 星期四：英文默書

## 🎮 核心功能

### Phase 1 - MVP（今晚完成）

1. **📷 OCR 輸入**
   - 上傳溫習範圍圖片
   - AI OCR 識別文字
   - 人手校正介面

2. **🔤 英文串字遊戲（Wordwall 風格）**
   - 顯示中文意思，串出英文
   - 打亂字母，重新排列
   - 計時挑戰模式

3. **📝 句子重組**
   - 打亂英文句子詞序
   - 拖拽重組正確句子

4. **✏️ 中文認字卡**
   - Flashcard 模式
   - 翻卡記憶遊戲

5. **🔊 發音功能**
   - Text-to-Speech 讀出詞語
   - 支援中英文發音

### Phase 2 - 進階功能（未來）

- 🏆 積分獎勵系統
- 📊 學習進度追蹤
- 👨‍👩‍👧 家長 Dashboard
- 🔗 GRWTH 整合（自動抓取功課）

## 🛠️ 技術架構

### Frontend
- **Framework:** Nuxt 3 + NUXT UI Pro
- **Template:** Dashboard
- **Styling:** Tailwind CSS
- **TTS:** Web Speech API

### Backend
- **API:** PostgREST (RESTful API from PostgreSQL)
- **Database:** PostgreSQL 15

### Infrastructure
- **Containerization:** Docker Compose
- **Reference:** Area2 postgresql-1 starter

## 📁 項目結構

```
spellquest/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── docs/
│   └── DEVELOPMENT_PLAN.md
├── frontend/
│   ├── nuxt.config.ts
│   ├── app.vue
│   ├── pages/
│   │   ├── index.vue
│   │   ├── spelling.vue
│   │   ├── sentence.vue
│   │   └── flashcard.vue
│   └── components/
│       ├── SpellingGame.vue
│       ├── SentenceGame.vue
│       └── FlashCard.vue
├── backend/
│   └── sql/
│       └── init.sql
└── screenshots/
    └── (cap 圖)
```

## 📅 開發時間表

| 時間 | 任務 |
|------|------|
| 01:00 | 開始通知 ✅ |
| 01:00-01:30 | 開發計劃書 + Create Repo |
| 01:30-02:30 | NUXT UI Pro 框架搭建 |
| 02:30-04:00 | 實現遊戲功能 |
| 04:00-05:00 | Docker Compose + 測試 |
| 05:00-05:30 | Cap 圖 + README |
| 05:30 | 完成通知 |

## 🎨 UI 設計方向

- 色彩鮮艷、童趣風格
- 大按鈕、大字體（適合小朋友）
- 動畫回饋（正確/錯誤）
- 星星/獎勵視覺效果

## 📊 數據庫設計

### Tables

```sql
-- 詞語表
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    chinese TEXT NOT NULL,
    english TEXT,
    pinyin TEXT,
    category VARCHAR(50),
    grade VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 句子表
CREATE TABLE sentences (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    translation TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 學習記錄
CREATE TABLE learning_records (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    correct BOOLEAN,
    time_spent INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ✅ 成功標準

- [ ] 可以輸入/上傳詞語
- [ ] 英文串字遊戲可玩
- [ ] 句子重組遊戲可玩
- [ ] 中文 Flashcard 可用
- [ ] 有發音功能
- [ ] Docker Compose 一鍵部署
- [ ] README 有截圖

---

**Let's build something cool for 沛晨！** 🚀
