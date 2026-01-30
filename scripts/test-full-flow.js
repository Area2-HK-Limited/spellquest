/**
 * Test full flow: Input words -> Start game
 */
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

async function testFullFlow() {
  console.log('🧪 Testing full flow: Input → Game\n');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Go to input page
    console.log('📄 Loading input page...');
    await page.goto('http://localhost:3003/input', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Find batch textarea and enter words (simulating OCR result)
    console.log('\n📝 Entering English words (dictation format)...');
    const batchTextarea = await page.locator('textarea').first();
    
    // Enter words in the format from the dictation sheet
    const words = `you
doing
talking
reading
book
running
grass
chatting
riding
bicycle
swimming
pool
having
fun`;
    
    await batchTextarea.fill(words);
    
    // Click batch add button
    const batchButton = await page.locator('button:has-text("批量新增")').first();
    await batchButton.click();
    await page.waitForTimeout(500);
    
    // Take screenshot of added words
    const addedPath = path.join(projectRoot, 'screenshots', 'flow-1-words-added.png');
    await page.screenshot({ path: addedPath, fullPage: true });
    console.log(`📸 Screenshot: ${addedPath}`);
    
    // Check if words were added
    const wordCount = await page.locator('.bg-gray-50.rounded-lg').count();
    console.log(`✅ Words added: ${wordCount}`);
    
    // Check for game buttons
    const spellingBtn = await page.locator('button:has-text("英文串字")').first();
    const spellingVisible = await spellingBtn.isVisible().catch(() => false);
    console.log(`✅ Spelling button visible: ${spellingVisible}`);
    
    if (spellingVisible) {
      // Click to start spelling game
      console.log('\n🎮 Starting spelling game...');
      await spellingBtn.click();
      await page.waitForTimeout(2000);
      
      // Check if we're on the spelling page
      const url = page.url();
      console.log(`📍 Current URL: ${url}`);
      
      // Take screenshot
      const gamePath = path.join(projectRoot, 'screenshots', 'flow-2-spelling-game.png');
      await page.screenshot({ path: gamePath, fullPage: true });
      console.log(`📸 Screenshot: ${gamePath}`);
      
      // Check if custom words are loaded
      const pageContent = await page.content();
      const hasCustomWords = words.split('\n').some(w => pageContent.includes(w));
      console.log(`✅ Custom words loaded: ${hasCustomWords}`);
    }
    
    console.log('\n✅ Full flow test completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    const errorPath = path.join(projectRoot, 'screenshots', 'flow-error.png');
    await page.screenshot({ path: errorPath, fullPage: true });
  } finally {
    await browser.close();
  }
}

testFullFlow();
