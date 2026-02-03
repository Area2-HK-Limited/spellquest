"""
SpellQuest OCR Service (AliCloud Qwen3-VL)
使用 AliCloud Model Studio Qwen3-VL 做 OCR
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os
from typing import List, Dict, Any
import json

app = FastAPI(
    title="SpellQuest OCR Service (AliCloud Qwen3-VL)",
    description="中英文 OCR 識別服務（使用 AliCloud Qwen3-VL）",
    version="2.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AliCloud Model Studio API
# Singapore region (default)
ALICLOUD_API = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY 環境變數未設定！")


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "SpellQuest OCR (AliCloud Qwen3-VL)",
        "model": "qwen3-vl-plus"
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
        
        # Call Qwen3-VL API
        prompt = """
請識別圖片中的所有文字，包括中文、英文、拼音。

返回 JSON 格式：
{
  "text": "完整文字內容",
  "words": ["詞語1", "詞語2", ...],
  "lines": ["第一行", "第二行", ...]
}
"""
        
        result = await call_qwen3_vl(image_b64, prompt)
        
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
        
        # Call Qwen3-VL API with structured prompt
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
        
        result = await call_qwen3_vl(image_b64, prompt)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"詞語提取失敗: {str(e)}")


async def call_qwen3_vl(image_b64: str, prompt: str) -> Dict[str, Any]:
    """
    Call AliCloud Qwen3-VL Vision API
    
    Args:
        image_b64: Base64 encoded image
        prompt: Text prompt
        
    Returns:
        Parsed JSON response from Qwen3-VL
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            ALICLOUD_API,
            headers={
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen3-vl-plus",
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
                detail=f"Qwen3-VL API 錯誤: {response.text}"
            )
        
        data = response.json()
        
        # Extract content from Qwen3-VL response
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON from content
        # Qwen may wrap JSON in markdown code blocks
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
        if not DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY not set")
        
        return {
            "status": "healthy",
            "model": "qwen3-vl-plus",
            "provider": "AliCloud Model Studio",
            "region": "Singapore (ap-southeast-1)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service 未正常運作: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
