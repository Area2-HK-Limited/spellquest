const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true,
    executablePath: '/home/ai-m01/.cache/ms-playwright/chromium-1208/chrome-linux/chrome'
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();
  
  const baseUrl = 'http://localhost:3002';
  const screenshotDir = '/home/ai-m01/clawd/projects/spellquest/screenshots';
  
  const pages = [
    { url: '/', name: 'home', desc: '主頁' },
    { url: '/spelling', name: 'spelling', desc: '英文串字' },
    { url: '/sentence', name: 'sentence', desc: '句子重組' },
    { url: '/flashcard', name: 'flashcard', desc: '中文認字' },
    { url: '/dictation', name: 'dictation', desc: '聽寫模式' },
    { url: '/matching', name: 'matching', desc: '配對遊戲' },
    { url: '/input', name: 'input', desc: '詞語輸入' },
    { url: '/words', name: 'words', desc: '詞語列表' },
    { url: '/stats', name: 'stats', desc: '學習進度' }
  ];
  
  for (const p of pages) {
    try {
      console.log(`Capturing ${p.desc} (${p.url})...`);
      await page.goto(baseUrl + p.url, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(1000);
      await page.screenshot({ 
        path: `${screenshotDir}/${p.name}.png`,
        fullPage: false
      });
      console.log(`✅ ${p.name}.png saved`);
    } catch (e) {
      console.log(`❌ ${p.name} failed: ${e.message}`);
    }
  }
  
  await browser.close();
  console.log('\nDone! Screenshots saved to:', screenshotDir);
})();
