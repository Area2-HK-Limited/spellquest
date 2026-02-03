"""
SpellQuest OCR Service (Tesseract)
使用 Tesseract OCR 做文字識別（免費開源方案）
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re
from typing import List, Dict, Any

app = FastAPI(
    title="SpellQuest OCR Service (Tesseract)",
    description="中英文 OCR 識別服務（使用 Tesseract OCR - 免費開源）",
    version="2.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "SpellQuest OCR (Tesseract)",
        "model": "tesseract-ocr"
    }


@app.post("/ocr/upload")
async def ocr_upload(file: UploadFile = File(...)):
    """
    上傳圖片進行 OCR 識別
    
    Returns:
    {
        "text": "識別的原始文字",
        "words": ["詞語1", "詞語2", ...],
        "lines": ["第一行", "第二行", ...]
    }
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只接受圖片檔案")
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # OCR with Tesseract (Chinese + English)
        text = pytesseract.image_to_string(image, lang='chi_tra+eng')
        
        # Parse text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        words = []
        
        for line in lines:
            # Extract words (split by spaces and filter out single chars)
            line_words = [w.strip() for w in re.split(r'[\s,，]+', line) if w.strip()]
            words.extend(line_words)
        
        return {
            "text": text.strip(),
            "words": words,
            "lines": lines
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 處理失敗: {str(e)}")


@app.post("/ocr/extract-vocab")
async def ocr_extract_vocab(file: UploadFile = File(...)):
    """
    上傳圖片並智能提取詞語
    適合默書範圍圖片 (詞語 + 英文翻譯 + 拼音)
    
    Returns:
    {
        "vocabulary": [
            {"chinese": "蘋果", "english": "apple", "pinyin": "píng guǒ"},
            ...
        ]
    }
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只接受圖片檔案")
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # OCR with Tesseract
        text = pytesseract.image_to_string(image, lang='chi_tra+eng')
        
        # Parse vocabulary
        vocabulary = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            # Try to parse format: "中文 english pinyin"
            # Remove numbering (1. 2. etc.)
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            
            # Split by spaces/commas
            parts = re.split(r'[\s,，]+', line)
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) == 0:
                continue
            
            # Detect Chinese, English, Pinyin
            chinese = ""
            english = ""
            pinyin = ""
            
            for part in parts:
                # Check if it's English (all ASCII letters)
                if re.match(r'^[a-zA-Z]+$', part):
                    if not english:
                        english = part
                # Check if it's Chinese (contains Chinese characters)
                elif re.search(r'[\u4e00-\u9fff]', part):
                    if not chinese:
                        chinese = part
                # Check if it's pinyin (lowercase + tone marks)
                elif re.match(r'^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+$', part, re.IGNORECASE):
                    if not pinyin:
                        pinyin = part
            
            # Only add if we have at least Chinese or English
            if chinese or english:
                vocabulary.append({
                    "chinese": chinese,
                    "english": english,
                    "pinyin": pinyin
                })
        
        return {
            "vocabulary": vocabulary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詞語提取失敗: {str(e)}")


@app.get("/health")
async def health_check():
    """健康檢查"""
    try:
        # Test Tesseract is available
        version = pytesseract.get_tesseract_version()
        
        return {
            "status": "healthy",
            "model": "tesseract-ocr",
            "version": str(version),
            "provider": "Tesseract (Open Source)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service 未正常運作: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
