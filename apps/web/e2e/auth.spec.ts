import { test, expect } from '@playwright/test'

const UNIQUE = Date.now()

test('register and login flow', async ({ page }) => {
  await page.goto('/register')
  await page.fill('input[type="email"]', `user${UNIQUE}@example.com`)
  await page.fill('input[placeholder*="мя"]', `User ${UNIQUE}`)
  await page.fill('input[type="password"]', 'password123')
  // slug field
  const slugInput = page.locator('input').nth(3)
  await slugInput.fill(`user-${UNIQUE}`)
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('/dashboard')
})

test('login with wrong password shows error', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[type="email"]', 'nobody@example.com')
  await page.fill('input[type="password"]', 'wrongpass')
  await page.click('button[type="submit"]')

  await expect(page.locator('text=/ошибка|неверн|not found/i')).toBeVisible({ timeout: 5000 })
})

test('unauthenticated redirect to login', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/login/)
})
