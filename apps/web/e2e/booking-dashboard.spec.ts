import { test, expect } from '@playwright/test'
import { createUser, createSchedule, getTomorrowISO } from './fixtures'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'

async function seedBooking(
  request: import('@playwright/test').APIRequestContext,
  token: string,
  userSlug: string,
  scheduleId: string,
): Promise<{ id: string; confirmationToken: string; cancelToken: string }> {
  const tomorrow = getTomorrowISO()
  const slotsRes = await request.get(
    `${API_URL}/public/${userSlug}/schedules/${scheduleId}/slots?date=${tomorrow}`,
  )
  const slots = await slotsRes.json()

  const bookingRes = await request.post(
    `${API_URL}/public/${userSlug}/schedules/${scheduleId}/bookings`,
    {
      data: {
        slotId: slots[0].id,
        guestName: 'Иван Тест',
        guestEmail: 'ivan@example.com',
        guestNote: 'Тестовое бронирование',
      },
    },
  )
  return bookingRes.json()
}

async function loginUser(page: import('@playwright/test').Page, email: string, password: string) {
  await page.goto('/login')
  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard', { timeout: 5000 })
}

test.describe('Bookings dashboard', () => {
  test('shows bookings list after login', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    await seedBooking(request, user.token, user.slug, schedule.id)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')
    await expect(page).toHaveURL('/bookings')

    // Default filter is "confirmed"; switch to "pending" to see the new booking
    await page.click('text=Ожидают')
    await expect(page.locator('[data-testid="booking-card"]').first()).toBeVisible({ timeout: 5000 })
    await expect(page.locator('text=Иван Тест')).toBeVisible()
    await expect(page.locator('text=ivan@example.com')).toBeVisible()
  })

  test('shows empty state when no bookings', async ({ page, request }) => {
    const user = await createUser(request)
    await createSchedule(request, user.token)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')

    await expect(page.locator('[data-testid="empty-bookings"]')).toBeVisible({ timeout: 5000 })
  })

  test('opens booking detail dialog on card click', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    await seedBooking(request, user.token, user.slug, schedule.id)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')
    await page.click('text=Ожидают')

    await page.locator('[data-testid="booking-card"]').first().click()
    const dialog = page.locator('[data-testid="booking-dialog"]')
    await expect(dialog.locator('text=ivan@example.com')).toBeVisible({ timeout: 3000 })
    await expect(dialog.locator('text=Тестовое бронирование')).toBeVisible()
  })

  test('host can confirm a pending booking', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    await seedBooking(request, user.token, user.slug, schedule.id)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')
    await page.click('text=Ожидают')

    await page.locator('[data-testid="booking-card"]').first().click()
    await page.locator('[data-testid="confirm-booking-btn"]').click()

    // Dialog closes after confirm; booking moves to "Подтверждены" filter
    await expect(page.locator('[data-testid="booking-dialog"]')).not.toBeVisible({ timeout: 5000 })
    await page.click('text=Подтверждены')
    await expect(page.locator('[data-testid="booking-card"]').first()).toBeVisible({ timeout: 5000 })
  })

  test('host can cancel a pending booking', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    await seedBooking(request, user.token, user.slug, schedule.id)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')
    await page.click('text=Ожидают')

    await page.locator('[data-testid="booking-card"]').first().click()
    // First click opens the cancel confirmation dialog
    await page.locator('[data-testid="cancel-booking-btn"]').click()
    // Confirm cancellation in the second dialog
    await page.locator('text=Отменить бронирование').last().click()

    // Booking moves to "Отменены" filter
    await page.click('text=Отменены')
    await expect(page.locator('[data-testid="booking-card"]').first()).toBeVisible({ timeout: 5000 })
  })

  test('status filter works', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    await seedBooking(request, user.token, user.slug, schedule.id)

    await loginUser(page, user.email, user.password)
    await page.click('text=Бронирования')

    // Default filter is "confirmed" — pending booking is hidden, empty state shown
    await expect(page.locator('[data-testid="empty-bookings"]')).toBeVisible({ timeout: 5000 })

    // Switch to "Ожидают" — pending booking should appear
    await page.click('text=Ожидают')
    await expect(page.locator('[data-testid="booking-card"]').first()).toBeVisible({ timeout: 3000 })

    // Switch to "Завершенные" — no past bookings, empty state
    await page.click('text=Завершенные')
    await expect(page.locator('[data-testid="empty-bookings"]')).toBeVisible({ timeout: 3000 })

    // Switch to "Отменены" — no cancelled bookings, empty state
    await page.click('text=Отменены')
    await expect(page.locator('[data-testid="empty-bookings"]')).toBeVisible({ timeout: 3000 })
  })
})
