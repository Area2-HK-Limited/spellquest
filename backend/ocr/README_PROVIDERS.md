# SpellQuest OCR Service - Multiple Providers

## 可用版本

| 檔案 | Provider | API Key 需求 | Accuracy | Cost |
|------|----------|--------------|----------|------|
| `main_alicloud_qwen3.py` | **AliCloud Qwen3-VL** | `DASHSCOPE_API_KEY` | ⭐⭐⭐⭐⭐ | $ |
| `main_anthropic.py` | Anthropic Claude | `ANTHROPIC_API_KEY` | ⭐⭐⭐⭐⭐ | $$$ |
| `main_openai.py` | OpenAI GPT-4o | `OPENAI_API_KEY` | ⭐⭐⭐⭐⭐ | $$$ |
| `main_tesseract.py` | Tesseract OCR | ❌ 免費 | ⭐⭐⭐ | 免費 |
| `main.py` (原版) | GitHub Copilot | `GITHUB_TOKEN` (Copilot) | ⭐⭐⭐⭐⭐ | - |

---

## 🎯 推薦：AliCloud Qwen3-VL（Eric 已提供 API Key）

**優點：**
- ✅ 支援 32 種語言 OCR（包括中英文）
- ✅ Eric 已經提供 API Key
- ✅ 成本較低（相比 Anthropic/OpenAI）
- ✅ 速度快
- ✅ 準確度高

**API Key:**
```
sk-d27e3f1d31504e51bf7d4623e51df5f0
```

---

## 使用方法

### ⭐ Option 0: AliCloud Qwen3-VL（推薦 - Eric 已提供 API Key）

**Eric 已經提供：**
- API Key: `sk-d27e3f1d31504e51bf7d4623e51df5f0`
- Region: Singapore (ap-southeast-1)
- Model: `qwen3-vl-plus`

**設定步驟：**

1. **設定環境變數:**
   ```bash
   export DASHSCOPE_API_KEY="sk-d27e3f1d31504e51bf7d4623e51df5f0"
   ```

2. **替換 main.py:**
   ```bash
   cd backend/ocr
   cp main_alicloud_qwen3.py main.py
   ```

3. **Restart service:**
   ```bash
   docker-compose restart ocr
   ```

**優點：**
- ✅ Eric 已經有 API key
- ✅ 成本較低（相比 Anthropic/OpenAI）
- ✅ 支援 32 種語言（包括中英文）
- ✅ 速度快

---

### Option 1: Anthropic Claude API

1. **取得 API Key:**
   - 去 https://console.anthropic.com/
   - 註冊/登入
   - Settings → API Keys → Create Key
   - Copy API key（格式：`sk-ant-xxx`）

2. **設定環境變數:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-xxxxx"
   ```

3. **替換 main.py:**
   ```bash
   cd backend/ocr
   cp main_anthropic.py main.py
   ```

4. **Restart service:**
   ```bash
   docker-compose restart ocr
   ```

---

### Option 2: OpenAI GPT-4o Vision

1. **取得 API Key:**
   - 去 https://platform.openai.com/api-keys
   - Create new secret key
   - Copy API key（格式：`sk-xxx`）

2. **設定環境變數:**
   ```bash
   export OPENAI_API_KEY="sk-xxxxx"
   ```

3. **替換 main.py:**
   ```bash
   cd backend/ocr
   cp main_openai.py main.py
   ```

4. **Restart service:**
   ```bash
   docker-compose restart ocr
   ```

---

### Option 3: Tesseract OCR（免費）

**優點：**
- ✅ 完全免費
- ✅ 無需 API key
- ✅ 開源

**缺點：**
- ⚠️ Accuracy 較低（特別係手寫文字）
- ⚠️ 需要高質素圖片

**使用方法：**

1. **安裝 Tesseract:**
   ```bash
   # Ubuntu/Debian
   apt-get install -y tesseract-ocr tesseract-ocr-chi-tra tesseract-ocr-eng
   
   # macOS
   brew install tesseract tesseract-lang
   ```

2. **替換 main.py:**
   ```bash
   cd backend/ocr
   cp main_tesseract.py main.py
   ```

3. **Restart service:**
   ```bash
   docker-compose restart ocr
   ```

---

## Dockerfile 修改

如果用 Tesseract，需要修改 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

# Install Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3002"]
```

---

## 測試

```bash
# Test health
curl http://localhost:3002/health

# Test OCR (upload image)
curl -X POST http://localhost:3002/ocr/extract-vocab \
  -F "file=@test_vocab.png"
```

---

## 建議

**Eric 的情況：**
- 如果有 Anthropic API key → 用 `main_anthropic.py`（最推薦）
- 如果有 OpenAI API key → 用 `main_openai.py`
- 如果唔想付錢 → 用 `main_tesseract.py`（免費但冇咁準）

**成本：**
- Anthropic/OpenAI: ~$0.01-0.03 per image（Claude 較平）
- Tesseract: 完全免費
