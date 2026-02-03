"""
SpellQuest OCR Service (Qwen-VL Vision)
使用 Alibaba DashScope API + Qwen-VL 做 OCR
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os
from typing import List, Dict, Any
import json

app = FastAPI(
    title="SpellQuest OCR Service (Qwen-VL)",
    description="中英文 OCR 識別服務（使用 Alibaba Qwen-VL）",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alibaba DashScope API
DASHSCOPE_API = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")

if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY 或 QWEN_API_KEY 環境變數未設定！")


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "SpellQuest OCR (Qwen-VL)",
        "model": "qwen-vl-max"
    }


async def call_qwen_vision(image_b64: str, prompt: str) -> Dict:
    """Call Qwen-VL API with image"""
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-vl-max",
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
        "max_tokens": 4096
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(DASHSCOPE_API, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Qwen API error: {response.text}"
            )
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


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
        
        # Call Qwen Vision API
        prompt = """
請識別圖片中的所有文字，包括中文、英文、拼音。
這是一份小學生的默書/詞語表。

請返回 JSON 格式（只返回 JSON，不要其他文字）：
{
  "text": "完整文字內容",
  "words": [
    {"chinese": "中文詞語", "english": "English word", "pinyin": "pīnyīn"}
  ],
  "lines": ["第一行", "第二行", ...]
}

如果某個欄位沒有內容，可以留空字串。
"""
        
        result = await call_qwen_vision(image_b64, prompt)
        
        # Parse JSON from response
        try:
            # Try to extract JSON from response
            if isinstance(result, str):
                # Find JSON in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {"text": result, "words": [], "lines": [result]}
            else:
                parsed = result
                
            return {
                "success": True,
                "data": parsed
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "data": {
                    "text": result,
                    "words": [],
                    "lines": [result]
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr/extract-vocab")
async def extract_vocabulary(file: UploadFile = File(...)):
    """
    從圖片中提取詞彙（專為默書設計）
    
    Returns:
    {
        "vocabulary": [
            {"chinese": "蘋果", "english": "apple", "pinyin": "píngguǒ"},
            ...
        ]
    }
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只接受圖片檔案")
    
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        prompt = """
請從這張圖片中提取所有詞彙。這是一份小學生的默書或詞語表。

請返回 JSON 格式（只返回 JSON，不要其他文字）：
{
  "vocabulary": [
    {"chinese": "中文詞語", "english": "English word", "pinyin": "pīnyīn"}
  ]
}

注意：
- 如果只有中文，english 和 pinyin 留空字串
- 如果只有英文，chinese 和 pinyin 留空字串
- 請識別所有可見的詞語
"""
        
        result = await call_qwen_vision(image_b64, prompt)
        
        try:
            if isinstance(result, str):
                import re
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {"vocabulary": []}
            else:
                parsed = result
                
            return {
                "success": True,
                "vocabulary": parsed.get("vocabulary", [])
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "無法解析 OCR 結果",
                "raw": result
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
