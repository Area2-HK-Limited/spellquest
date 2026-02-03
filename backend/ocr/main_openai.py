"""
SpellQuest OCR Service (OpenAI GPT-4o Vision)
使用 OpenAI GPT-4o Vision 做 OCR
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os
from typing import List, Dict, Any
import json

app = FastAPI(
    title="SpellQuest OCR Service (OpenAI GPT-4o)",
    description="中英文 OCR 識別服務（使用 OpenAI GPT-4o Vision）",
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

# OpenAI API
OPENAI_API = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 環境變數未設定！")


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "SpellQuest OCR (OpenAI GPT-4o)",
        "model": "gpt-4o"
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
        # Read and encode image
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        # Call OpenAI API
        prompt = """
請識別圖片中的所有文字，包括中文、英文、拼音。

返回 JSON 格式：
{
  "text": "完整文字內容",
  "words": ["詞語1", "詞語2", ...],
  "lines": ["第一行", "第二行", ...]
}
"""
        
        result = await call_gpt4o_vision(image_b64, prompt)
        
        return result
        
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
        # Read and encode image
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        # Call OpenAI API with structured prompt
        prompt = """
請識別圖片中的詞語列表，並提取每個詞語的：
1. 中文
2. 英文翻譯
3. 拼音（如果有）

常見格式：
- "蘋果 apple píng guǒ"
- "1. 蘋果 (apple) píng guǒ"
- "蘋果 apple"

返回 JSON 格式：
{
  "vocabulary": [
    {
      "chinese": "蘋果",
      "english": "apple",
      "pinyin": "píng guǒ"
    },
    ...
  ]
}

注意：
- 如果沒有拼音，pinyin 返回空字串
- 忽略序號（1. 2. 等）
- 每個詞語必須有中文或英文
"""
        
        result = await call_gpt4o_vision(image_b64, prompt)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詞語提取失敗: {str(e)}")


async def call_gpt4o_vision(image_b64: str, prompt: str) -> Dict[str, Any]:
    """
    Call OpenAI GPT-4o Vision API
    
    Args:
        image_b64: Base64 encoded image
        prompt: Text prompt
        
    Returns:
        Parsed JSON response from GPT-4o
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENAI_API,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API 錯誤: {response.text}"
            )
        
        data = response.json()
        
        # Extract content from OpenAI response
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON from content
        # GPT may wrap JSON in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        return result


@app.get("/health")
async def health_check():
    """健康檢查"""
    try:
        # Test API key is set
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        
        return {
            "status": "healthy",
            "model": "gpt-4o",
            "provider": "OpenAI"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service 未正常運作: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
