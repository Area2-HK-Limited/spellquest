/**
 * Test memory tip feature
 */
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

async function testMemoryTip() {
  console.log('🧪 Testing memory tip feature\n');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Go to input page and add words
    await page.goto('http://localhost:3003/input', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Enter words
    const batchTextarea = await page.locator('textarea').first();
    await batchTextarea.fill('you\nrunning\nswimming');
    
    const batchButton = await page.locator('button:has-text("批量新增")').first();
    await batchButton.click();
    await page.waitForTimeout(500);
    
    // Start spelling game
    const spellingBtn = await page.locator('button:has-text("英文串字")').first();
    await spellingBtn.click();
    await page.waitForTimeout(2000);
    
    // Click letters to spell "you": y, o, u
    // The letters are scrambled, so we need to click in order
    console.log('📝 Spelling "you"...');
    
    // Get all letter buttons
    const letterButtons = page.locator('.sq-card button.text-2xl');
    const count = await letterButtons.count();
    console.log(`Found ${count} letter buttons`);
    
    // Click y, o, u in order
    for (const letter of ['y', 'o', 'u']) {
      const btn = page.locator(`.sq-card button.text-2xl:has-text("${letter}")`).first();
      if (await btn.isVisible()) {
        await btn.click();
        await page.waitForTimeout(200);
      }
    }
    
    // Take screenshot before confirming
    await page.screenshot({ 
      path: path.join(projectRoot, 'screenshots', 'memory-tip-1-before.png'), 
      fullPage: true 
    });
    
    // Click confirm
    const confirmBtn = page.locator('button:has-text("確認答案")').first();
    await confirmBtn.click();
    await page.waitForTimeout(1000);
    
    // Take screenshot after confirming (should show memory tip)
    await page.screenshot({ 
      path: path.join(projectRoot, 'screenshots', 'memory-tip-2-after.png'), 
      fullPage: true 
    });
    
    // Check if memory tip is visible
    const tipVisible = await page.locator('text=記憶小貼士').isVisible();
    console.log(`✅ Memory tip visible: ${tipVisible}`);
    
    // Get the tip text
    const tipText = await page.locator('.bg-yellow-50 p.text-yellow-800').textContent().catch(() => '');
    console.log(`💡 Tip: ${tipText}`);
    
    console.log('\n✅ Test completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ 
      path: path.join(projectRoot, 'screenshots', 'memory-tip-error.png'), 
      fullPage: true 
    });
  } finally {
    await browser.close();
  }
}

testMemoryTip();
