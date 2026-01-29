# SpellQuest OCR Service

中英文 OCR 識別服務，使用 Tesseract OCR。

## 🚀 快速開始

```bash
# Build
docker build -t spellquest-ocr .

# Run
docker run -p 3002:3002 spellquest-ocr
```

## 📡 API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. 基本 OCR
```bash
POST /ocr/upload
Content-Type: multipart/form-data

# Response
{
  "text": "識別的原始文字",
  "words": ["詞語1", "詞語2", ...],
  "lines": ["第一行", "第二行", ...],
  "image_size": [width, height]
}
```

### 3. 智能詞語提取
```bash
POST /ocr/extract-vocab
Content-Type: multipart/form-data

# Response
{
  "vocabulary": [
    {
      "chinese": "蘋果",
      "english": "apple",
      "pinyin": "píng guǒ"
    },
    ...
  ],
  "raw_text": "原始OCR文字"
}
```

## 🧪 測試

```bash
# 上傳圖片測試
curl -X POST "http://localhost:3002/ocr/upload" \
  -F "file=@test.jpg"

# 詞語提取測試
curl -X POST "http://localhost:3002/ocr/extract-vocab" \
  -F "file=@vocabulary.jpg"
```

## 🔧 支援的語言

- 繁體中文 (chi_tra)
- 簡體中文 (chi_sim)
- 英文 (eng)

## 📝 詞語格式支援

OCR 可以識別以下格式：

```
蘋果 apple píng guǒ
香蕉 banana xiāng jiāo
橙 orange chéng
```

或

```
1. 蘋果 (apple) píng guǒ
2. 香蕉 (banana) xiāng jiāo
3. 橙 (orange) chéng
```

## ⚙️ 配置

- `--psm 6`: Assume uniform block of text
- `lang='chi_tra+eng'`: 繁體中文 + 英文混合識別
