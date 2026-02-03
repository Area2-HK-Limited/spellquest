import { test, expect } from '@playwright/test';

const BASE_URL = 'http://192.168.139.142:3000';

test.describe('SpellQuest UI Tests', () => {
  
  test('Home page - should display game cards and they should be clickable', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Check title
    await expect(page).toHaveTitle(/SpellQuest/);
    
    // Check welcome text
    await expect(page.getByText('歡迎返嚟！')).toBeVisible();
    
    // Check game section header
    await expect(page.getByText('遊戲模式')).toBeVisible();
    
    // Check game cards exist
    await expect(page.getByText('英文串字')).toBeVisible();
    await expect(page.getByText('句子重組')).toBeVisible();
    await expect(page.getByText('中文認字')).toBeVisible();
    
    // Check tools section
    await expect(page.getByText('工具')).toBeVisible();
    await expect(page.getByRole('heading', { name: '輸入詞語' })).toBeVisible();
    await expect(page.getByRole('heading', { name: '詞語列表' })).toBeVisible();
    
    // Test navigation to Words page
    await page.click('text=詞語列表');
    await expect(page).toHaveURL(/\/words/);
  });

  test('Words page - should display table with data', async ({ page }) => {
    await page.goto(`${BASE_URL}/words`);
    
    // Check page loaded
    await expect(page.getByRole('heading', { name: /詞語列表/ })).toBeVisible();
    
    // Wait for table to load
    await page.waitForTimeout(2000);
    
    // Check table exists (UTable renders a table element)
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('Input page - should display form elements', async ({ page }) => {
    await page.goto(`${BASE_URL}/input`);
    
    // Check page loaded - look for main heading
    await expect(page.getByRole('heading', { name: '📷 輸入詞語' })).toBeVisible();
    
    // Check for input fields or buttons
    const inputFields = page.locator('input');
    await expect(inputFields.first()).toBeVisible();
  });

  test('Spelling page - should load spelling game', async ({ page }) => {
    await page.goto(`${BASE_URL}/spelling`);
    
    // Check page loaded
    await expect(page).toHaveURL(/\/spelling/);
    
    // Wait for content
    await page.waitForTimeout(1000);
    
    // Page should have some content (not just empty)
    const body = page.locator('body');
    await expect(body).not.toBeEmpty();
  });

  test('Navigation - sidebar collapse button should exist', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Look for specific sidebar button
    const collapseBtn = page.getByRole('button', { name: 'Collapse sidebar' });
    const openBtn = page.getByRole('button', { name: 'Open sidebar' });
    
    // At least one should exist
    const collapseVisible = await collapseBtn.isVisible().catch(() => false);
    const openVisible = await openBtn.isVisible().catch(() => false);
    
    expect(collapseVisible || openVisible).toBeTruthy();
  });

});
