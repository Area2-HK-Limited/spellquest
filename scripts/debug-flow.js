/**
 * Debug localStorage flow
 */
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

async function debugFlow() {
  console.log('🔍 Debugging localStorage flow\n');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Go to input page
    await page.goto('http://localhost:3003/input', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Enter words
    const batchTextarea = await page.locator('textarea').first();
    await batchTextarea.fill('you\ndoing\ntalking\nreading');
    
    const batchButton = await page.locator('button:has-text("批量新增")').first();
    await batchButton.click();
    await page.waitForTimeout(500);
    
    // Check localStorage before clicking game button
    const beforeClick = await page.evaluate(() => {
      return {
        practice_words: localStorage.getItem('spellquest_practice_words'),
        practice_mode: localStorage.getItem('spellquest_practice_mode')
      };
    });
    console.log('Before clicking game:', beforeClick);
    
    // Click spelling button
    const spellingBtn = await page.locator('button:has-text("英文串字")').first();
    await spellingBtn.click();
    await page.waitForTimeout(1000);
    
    // Check localStorage after navigation
    const afterClick = await page.evaluate(() => {
      return {
        practice_words: localStorage.getItem('spellquest_practice_words'),
        practice_mode: localStorage.getItem('spellquest_practice_mode')
      };
    });
    console.log('After navigation:', afterClick);
    
    // Check current URL
    console.log('URL:', page.url());
    
    // Take screenshot
    await page.screenshot({ 
      path: path.join(projectRoot, 'screenshots', 'debug-spelling.png'), 
      fullPage: true 
    });
    
  } finally {
    await browser.close();
  }
}

debugFlow();
