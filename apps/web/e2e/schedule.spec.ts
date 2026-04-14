import { test, expect } from '@playwright/test'
import { createUser } from './fixtures'

async function loginUser(page: import('@playwright/test').Page, email: string, password: string) {
  await page.goto('/login')
  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard', { timeout: 5000 })
}

test.describe('Schedules dashboard', () => {
  test('creates a new schedule via form', async ({ page, request }) => {
    const user = await createUser(request)
    await loginUser(page, user.email, user.password)

    // Open create dialog
    await page.click('text=Новое событие')
    await expect(page.locator('[data-testid="booking-dialog"]')).toBeVisible()

    // Fill name
    await page.fill('#name', 'Тест E2E Событие')

    // Select duration from dropdown
    await page.selectOption('#duration', '45')

    // Submit
    await page.click('button[type="submit"]')

    // Card appears in grid
    await expect(page.locator('text=Тест E2E Событие')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('text=45 мин')).toBeVisible()
  })

  test('edits an existing schedule', async ({ page, request }) => {
    const user = await createUser(request)
    await loginUser(page, user.email, user.password)

    // Create schedule via form first
    await page.click('text=Новое событие')
    await page.fill('#name', 'Исходное событие')
    await page.click('button[type="submit"]')
    await expect(page.locator('text=Исходное событие')).toBeVisible({ timeout: 5000 })

    // Click edit button on the card (pencil icon button)
    const card = page.locator('.grid > div').filter({ hasText: 'Исходное событие' })
    await card.locator('button').nth(2).click()

    await expect(page.locator('[data-testid="booking-dialog"]')).toBeVisible()

    // Change name
    await page.fill('#name', 'Изменённое событие')
    await page.click('button[type="submit"]')

    await expect(page.locator('text=Изменённое событие')).toBeVisible({ timeout: 5000 })
  })

  test('deletes schedule only after confirmation', async ({ page, request }) => {
    const user = await createUser(request)
    await loginUser(page, user.email, user.password)

    // Create schedule via form
    await page.click('text=Новое событие')
    await page.fill('#name', 'Событие для удаления')
    await page.click('button[type="submit"]')
    await expect(page.locator('text=Событие для удаления')).toBeVisible({ timeout: 5000 })

    // Click delete icon on the card
    const card = page.locator('.grid > div').filter({ hasText: 'Событие для удаления' })
    await card.locator('button').last().click()

    // Confirmation dialog must appear
    await expect(page.locator('[data-testid="booking-dialog"]')).toBeVisible()
    await expect(page.locator('text=Удалить событие')).toBeVisible()

    // Cancel — schedule should still be there
    await page.click('text=Отмена')
    await expect(page.locator('text=Событие для удаления')).toBeVisible()

    // Delete again and confirm
    await card.locator('button').last().click()
    await page.locator('[data-testid="confirm-delete-btn"]').click()

    // Schedule removed
    await expect(page.locator('text=Событие для удаления')).not.toBeVisible({ timeout: 5000 })
  })
})
