# 貢獻指南 Contributing Guide

歡迎參與 SpellQuest 開發！🎮

## 🚀 快速開始

### 1. Clone 項目

```bash
git clone https://github.com/Area2-HK-Limited/spellquest.git
cd spellquest
```

### 2. 本地開發

```bash
cd frontend
npm install
npm run dev
```

打開 http://localhost:3000

### 3. 用 Docker

```bash
docker-compose up -d
```

## 📋 分工

### M01 Router（主要開發）
- 🎮 遊戲邏輯同新功能
- 📊 學習數據分析
- 🧪 測試 + 部署
- 📝 文檔維護

### W01 頭皮（UI/UX）
- 🎨 介面美化
- ✨ 動畫效果（答對/答錯回饋）
- 🏆 獎勵特效（星星、煙花）
- 📱 Mobile responsive
- 🔊 優化 TTS 發音

### W02 面油（Backend）
- 🗄️ PostgREST API 整合
- 📷 OCR 功能（Tesseract.js）
- 🔗 GRWTH 整合（自動抓取功課）
- 💾 數據持久化

## 🌿 Git 工作流

### Branch 命名

```
feature/xxx    # 新功能
fix/xxx        # Bug 修復
ui/xxx         # UI 改善
```

### Commit 格式

```
feat: 新功能
fix: Bug 修復
ui: UI 改善
docs: 文檔更新
refactor: 重構
```

例子：
```bash
git commit -m "feat: Add matching game"
git commit -m "ui: Add success animation"
git commit -m "fix: TTS not working on Safari"
```

### 開發流程

```bash
# 1. 建立新 branch
git checkout -b feature/your-feature

# 2. 開發 + commit
git add .
git commit -m "feat: Your feature"

# 3. Push
git push origin feature/your-feature

# 4. 開 PR 或者直接 merge（小改動）
git checkout main
git merge feature/your-feature
git push
```

## 📁 項目結構

```
frontend/
├── pages/           # 頁面（自動路由）
│   ├── index.vue    # 主頁
│   ├── spelling.vue # 英文串字
│   └── ...
├── components/      # 可重用組件
├── composables/     # Vue composables
├── assets/css/      # 全局樣式
└── public/          # 靜態資源
```

## 🎨 UI 設計原則

1. **大按鈕、大字體** - 適合小朋友
2. **鮮艷色彩** - 吸引注意力
3. **即時回饋** - 答對/答錯要有動畫
4. **獎勵機制** - 星星、徽章、音效

## 🔊 TTS 使用

```javascript
const speak = (text, lang = 'zh-TW') => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang  // 'zh-TW' 或 'en-US'
    utterance.rate = 0.8   // 慢啲，小朋友聽得清
    window.speechSynthesis.speak(utterance)
  }
}
```

## 📡 API 整合（TODO）

```javascript
// composables/useApi.js
const config = useRuntimeConfig()

export const useApi = () => {
  const baseUrl = config.public.apiUrl
  
  const getWords = () => $fetch(`${baseUrl}/words`)
  const addWord = (word) => $fetch(`${baseUrl}/words`, {
    method: 'POST',
    body: word
  })
  
  return { getWords, addWord }
}
```

## 🐛 常見問題

### TTS 唔出聲？
- Safari 需要用戶先互動（click）先可以播放
- 用 `speechSynthesis.cancel()` 清除之前嘅隊列

### NUXT UI Pro 組件用法？
- 參考：https://ui.nuxt.com/

## 📞 溝通

- Discord #ai-team-group
- @ 對方確保收到通知

---

有問題隨時喺 team channel 問！💪
