"""
SpellQuest OCR Service (Qwen-VL Vision & Image Generation & TTS)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import httpx
import base64
import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
import asyncio
from pathlib import Path
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SpellQuest Services (OCR + ImageGen + TTS)",
    description="OCR (Qwen-VL), Image Generation (Wanx-v1), and TTS (CosyVoice) services",
    version="2.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")
if not DASHSCOPE_API_KEY:
    logger.warning("DASHSCOPE_API_KEY/QWEN_API_KEY not set!")

# OCR API URL
DASHSCOPE_OCR_API = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# Directories
IMAGES_DIR = Path("/app/images")
AUDIO_DIR = Path("/app/audio")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Mount static directories
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# --- Models ---
class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    voice: str = "longxiaochun"

class ImageGenRequest(BaseModel):
    word: str
    force: bool = False

# --- Helper Functions ---

async def call_qwen_vision(image_b64: str, prompt: str) -> Dict:
    """Call Qwen-VL API with image (OCR)"""
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
        response = await client.post(DASHSCOPE_OCR_API, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Qwen API error: {response.text}"
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Try to parse JSON from markdown code block if present
        try:
            if isinstance(content, str):
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
                return {"text": content} # Fallback
            return content
        except:
            return content

async def download_file(url: str, dest_path: Path):
    """Download file from URL to local path"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(resp.content)
        else:
            logger.error(f"Failed to download: {url}")

# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "SpellQuest Backend Services",
        "features": ["ocr", "image-generation", "tts"]
    }

# 1. OCR Endpoints
@app.post("/ocr/upload")
async def ocr_upload(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image only")
    
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        prompt = """
請識別圖片中的所有文字。
返回 JSON:
{
  "text": "完整文字",
  "words": [{"chinese": "中文", "english": "eng", "pinyin": "py"}],
  "lines": ["row1", "row2"]
}
"""
        result = await call_qwen_vision(image_b64, prompt)
        return {"success": True, "data": result}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr/extract-vocab")
async def extract_vocabulary(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image only")
    
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode('utf-8')
        
        prompt = """
提取詞彙。
返回 JSON:
{
  "vocabulary": [{"chinese": "中文", "english": "eng", "pinyin": "py"}]
}
"""
        result = await call_qwen_vision(image_b64, prompt)
        return {"success": True, "vocabulary": result.get("vocabulary", [])}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. Image Generation (Z-Image-Turbo / Wanx)
@app.post("/generate-image")
async def generate_image(req: ImageGenRequest):
    """
    Generate image for a word using Wanx-v1.
    """
    word = req.word.strip().lower()
    filename = f"{word}.png"
    local_path = IMAGES_DIR / filename
    local_url = f"/images/{filename}"

    if not req.force and local_path.exists():
        return {"url": local_url, "cached": True}

    api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": f"Cartoon illustration of {word}, cute style, white background, for kids education, simple, colorful"
        },
        "parameters": {
            "style": "<auto>",
            "size": "1024*1024",
            "n": 1
        }
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Start Task
            resp = await client.post(api_url, headers=headers, json=payload)
            data = resp.json()
            
            if "output" not in data or "task_id" not in data["output"]:
                 raise HTTPException(500, f"Failed to start gen task: {data}")
            
            task_id = data["output"]["task_id"]
            
            # Poll for result (max 30s)
            for _ in range(10):
                await asyncio.sleep(2)
                task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
                task_resp = await client.get(task_url, headers=headers)
                task_data = task_resp.json()
                
                if task_data["output"]["task_status"] == "SUCCEEDED":
                    img_url = task_data["output"]["results"][0]["url"]
                    await download_file(img_url, local_path)
                    return {"url": local_url, "cached": False}
                
                if task_data["output"]["task_status"] == "FAILED":
                    raise HTTPException(500, "Generation failed")
            
            raise HTTPException(504, "Generation timed out")

    except Exception as e:
        logger.error(f"Image gen error: {e}")
        return {"url": f"https://placehold.co/400x400?text={word}", "fallback": True}


# 3. TTS (CosyVoice)
@app.post("/tts")
async def text_to_speech(req: TTSRequest):
    """
    Generate speech using CosyVoice.
    """
    text_hash = hashlib.md5(f"{req.text}-{req.speed}".encode()).hexdigest()
    filename = f"{text_hash}.mp3"
    local_path = AUDIO_DIR / filename
    local_url = f"/audio/{filename}"
    
    if local_path.exists():
        return {"url": local_url, "cached": True}

    api_url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/generation"
    
    payload = {
        "model": "cosyvoice-v1",
        "input": {
            "text": req.text
        },
        "parameters": {
            "voice": "longxiaochun",
            "format": "mp3",
            "sample_rate": 22050,
            "volume": 50,
            "rate": req.speed
        }
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(api_url, headers=headers, json=payload)
            
            if resp.status_code == 200:
                if resp.headers.get("content-type") == "audio/mpeg":
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                    return {"url": local_url, "cached": False}
                else:
                    data = resp.json()
                    raise HTTPException(500, f"TTS API Error: {data}")
            else:
                 raise HTTPException(resp.status_code, f"TTS API Error: {resp.text}")

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
