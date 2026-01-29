"""
SpellQuest OCR Service
使用 Tesseract OCR 識別中英文混合文字
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
from typing import List, Dict, Any

app = FastAPI(
    title="SpellQuest OCR Service",
    description="中英文 OCR 識別服務",
    version="1.0.0"
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
    return {"status": "ok", "service": "SpellQuest OCR"}


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
        
        # OCR with Chinese + English
        text = pytesseract.image_to_string(
            image,
            lang='chi_tra+eng',  # 繁體中文 + 英文
            config='--psm 6'      # Assume uniform block of text
        )
        
        # Clean text
        text = text.strip()
        
        # Split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract words (split by whitespace/punctuation)
        words = extract_words(text)
        
        return {
            "text": text,
            "words": words,
            "lines": lines,
            "image_size": image.size
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
        
        # OCR
        text = pytesseract.image_to_string(
            image,
            lang='chi_tra+eng',
            config='--psm 6'
        )
        
        # Parse vocabulary
        vocabulary = parse_vocabulary(text)
        
        return {
            "vocabulary": vocabulary,
            "raw_text": text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詞語提取失敗: {str(e)}")


def extract_words(text: str) -> List[str]:
    """
    從文字中提取詞語
    """
    # Remove punctuation but keep Chinese characters and English words
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
    return list(set(words))  # Remove duplicates


def parse_vocabulary(text: str) -> List[Dict[str, str]]:
    """
    智能解析詞語列表
    支持格式:
    - "蘋果 apple píng guǒ"
    - "蘋果 (apple) píng guǒ"
    - "1. 蘋果 apple"
    """
    vocabulary = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove numbering (1. 2. etc.)
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        
        # Try to extract Chinese, English, Pinyin
        # Pattern: Chinese characters, followed by English, optionally followed by Pinyin
        chinese_match = re.search(r'[\u4e00-\u9fff]+', line)
        english_match = re.search(r'\b[a-zA-Z\s]+\b', line)
        pinyin_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+\s+[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+', line, re.IGNORECASE)
        
        if chinese_match:
            chinese = chinese_match.group().strip()
            english = english_match.group().strip() if english_match else ""
            pinyin = pinyin_match.group().strip() if pinyin_match else ""
            
            # Skip if too short
            if len(chinese) < 2:
                continue
            
            vocabulary.append({
                "chinese": chinese,
                "english": english,
                "pinyin": pinyin
            })
    
    return vocabulary


@app.get("/health")
async def health_check():
    """健康檢查"""
    try:
        # Test Tesseract is working
        version = pytesseract.get_tesseract_version()
        return {
            "status": "healthy",
            "tesseract_version": str(version)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tesseract 未正常運作: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
