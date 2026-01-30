# Database Migration Guide

## 📋 Overview

SpellQuest 嘅 database schema 分兩部分：
1. **`init.sql`** - Tables, indexes, sample data
2. **`functions.sql`** - Custom PostgreSQL functions, views

## 🚀 Fresh Install (新部署)

如果你係第一次 deploy，`functions.sql` 會自動執行：

```bash
docker-compose up -d
```

`docker-entrypoint-initdb.d` 會按順序執行：
1. `01-init.sql` → 建立 tables
2. `02-functions.sql` → 建立 functions

---

## 🔄 Apply Functions to Existing Database (更新 functions)

如果 database 已經 running，想 apply 新嘅 functions：

### Option 1: 用 migration script（推薦）

```bash
./scripts/apply-functions.sh
```

### Option 2: 手動執行

```bash
docker exec -i spellquest_db psql -U postgres -d spellquest < backend/sql/functions.sql
```

---

## 🗑️ Reset Database (清空數據重建)

⚠️ **警告：會清空所有數據！**

```bash
# Stop containers
docker-compose down

# Remove database volume
rm -rf postgres_data/

# Start fresh
docker-compose up -d
```

---

## ✅ Verify Functions

```bash
# List all custom functions
docker exec -it spellquest_db psql -U postgres -d spellquest -c '\df'

# Test get_random_words
docker exec -it spellquest_db psql -U postgres -d spellquest -c \
  "SELECT * FROM get_random_words('fruit', 'P1', 5);"

# Test word_accuracy_stats view
docker exec -it spellquest_db psql -U postgres -d spellquest -c \
  "SELECT * FROM word_accuracy_stats LIMIT 5;"
```

---

## 📝 Available Functions

| Function | Description |
|----------|-------------|
| `get_random_words(category, grade, limit)` | 隨機抽詞語 |
| `get_quiz_questions(word_set_id)` | 生成題目 |
| `submit_learning_record(word_id, game_type, correct, time_ms)` | 提交學習記錄 |
| `get_random_sentences(category, grade, limit)` | 隨機抽句子 |
| `get_word_set_details(word_set_id)` | 詞語集詳情 |
| `bulk_insert_words(jsonb)` | 批量插入詞語 |

## 📊 Available Views

| View | Description |
|------|-------------|
| `word_accuracy_stats` | 詞語準確率統計 |
| `learning_progress` | 學習進度 |

---

## 🐛 Troubleshooting

### Functions not found after deploy

**原因：** Database 已經 initialized，`docker-entrypoint-initdb.d` 只會執行一次。

**解決：**
```bash
./scripts/apply-functions.sh
```

### Permission denied

**原因：** Script 冇 execute 權限。

**解決：**
```bash
chmod +x scripts/apply-functions.sh
```

### Container not running

**原因：** PostgreSQL container 未啟動。

**解決：**
```bash
docker-compose up -d postgres
```

---

## 📚 Further Reading

- [PostgREST Custom Functions](https://postgrest.org/en/stable/api.html#stored-procedures)
- [PostgreSQL Functions](https://www.postgresql.org/docs/current/sql-createfunction.html)
