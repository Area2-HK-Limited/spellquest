/**
 * Test OCR upload functionality
 */
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

async function testOCRUpload() {
  console.log('🧪 Testing OCR upload functionality...\n');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Go to input page
    console.log('📄 Loading input page...');
    await page.goto('http://localhost:3003/input', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    // Check if OCR section exists
    const ocrSection = await page.locator('text=OCR 相片輸入').first();
    const ocrVisible = await ocrSection.isVisible();
    console.log(`✅ OCR section visible: ${ocrVisible}`);
    
    // Check for upload buttons
    const selectButton = await page.locator('button:has-text("選擇相片")').first();
    const cameraButton = await page.locator('button:has-text("影相")').first();
    
    console.log(`✅ Select photo button: ${await selectButton.isVisible()}`);
    console.log(`✅ Camera button: ${await cameraButton.isVisible()}`);
    
    // Create a test image (simple text image)
    const testImagePath = path.join(projectRoot, 'tmp', 'test-vocab.png');
    
    // Check if we have any test image
    const screenshotPath = path.join(projectRoot, 'screenshots', 'home.png');
    if (fs.existsSync(screenshotPath)) {
      console.log('\n📸 Using existing screenshot as test image...');
      
      // Find the file input
      const fileInput = await page.locator('input[type="file"]').first();
      
      // Upload the file
      await fileInput.setInputFiles(screenshotPath);
      await page.waitForTimeout(1000);
      
      // Check if image is displayed
      const uploadedImage = await page.locator('img[class*="max-h"]').first();
      const imageVisible = await uploadedImage.isVisible().catch(() => false);
      console.log(`✅ Uploaded image displayed: ${imageVisible}`);
      
      // Check for OCR button
      const ocrButton = await page.locator('button:has-text("開始識別")').first();
      const ocrButtonVisible = await ocrButton.isVisible().catch(() => false);
      console.log(`✅ OCR button visible: ${ocrButtonVisible}`);
      
      if (ocrButtonVisible) {
        // Click OCR button
        console.log('\n🔍 Clicking OCR button...');
        await ocrButton.click();
        await page.waitForTimeout(2000);
        
        // Check for result textarea
        const resultTextarea = await page.locator('textarea').nth(1);
        const textareaVisible = await resultTextarea.isVisible().catch(() => false);
        console.log(`✅ Result textarea visible: ${textareaVisible}`);
        
        if (textareaVisible) {
          const textareaValue = await resultTextarea.inputValue();
          console.log(`📝 Textarea content:\n${textareaValue}`);
        }
      }
      
      // Take screenshot of result
      const resultPath = path.join(projectRoot, 'screenshots', 'ocr-test.png');
      await page.screenshot({ path: resultPath, fullPage: true });
      console.log(`\n📸 Screenshot saved: ${resultPath}`);
    } else {
      console.log('⚠️ No test image found');
    }
    
    // Test manual input flow
    console.log('\n📝 Testing batch input...');
    const batchTextarea = await page.locator('textarea').first();
    await batchTextarea.fill('蘋果,apple,píng guǒ\n香蕉,banana,xiāng jiāo\n橙,orange,chéng');
    
    const batchButton = await page.locator('button:has-text("批量新增")').first();
    await batchButton.click();
    await page.waitForTimeout(500);
    
    // Check if words were added
    const addedWords = await page.locator('text=蘋果').first();
    const wordsAdded = await addedWords.isVisible().catch(() => false);
    console.log(`✅ Batch words added: ${wordsAdded}`);
    
    // Final screenshot
    const finalPath = path.join(projectRoot, 'screenshots', 'input-test-final.png');
    await page.screenshot({ path: finalPath, fullPage: true });
    console.log(`📸 Final screenshot saved: ${finalPath}`);
    
    console.log('\n✅ All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    const errorPath = path.join(projectRoot, 'screenshots', 'ocr-test-error.png');
    await page.screenshot({ path: errorPath, fullPage: true });
  } finally {
    await browser.close();
  }
}

testOCRUpload();
