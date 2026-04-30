import { test, expect } from '@playwright/test'
import { createUser, createSchedule, getTomorrowISO } from './fixtures'

const API_URL = process.env.API_URL ?? 'http://localhost:8000'

test.describe('Public booking flow', () => {
  test('full flow: profile → slot picker → form → confirmation page', async ({
    page,
    request,
  }) => {
    // Seed: create host user + schedule via API
    const user = await createUser(request)
    await createSchedule(request, user.token)

    // 1. Visit public profile
    await page.goto(`/book/${user.slug}`)
    await expect(page.locator('h1')).toContainText(user.name)
    await expect(page.locator('text=E2E Консультация')).toBeVisible()

    // 2. Click on schedule
    await page.click('text=Выбрать время')
    await expect(page).toHaveURL(new RegExp(`/book/${user.slug}/schedules/.+/slots`))

    // 3. Pick a date — click on first available day in the calendar
    const availableDay = page.locator('[data-testid="calendar-day-available"]').first()
    await expect(availableDay).toBeVisible({ timeout: 10000 })
    await availableDay.click()

    // Wait for slots to load
    await expect(page.locator('text=Выберите время')).toBeVisible({ timeout: 5000 })

    // 4. Pick first available slot
    const slotButtons = page.locator('[data-testid="slot-grid"] button:not([disabled])').first()
    await slotButtons.click()

    // 5. Click Продолжить
    await page.click('text=Продолжить')
    await expect(page).toHaveURL(new RegExp(`/book/${user.slug}/schedules/.+/book`))

    // 6. Fill in guest form
    await page.fill('#guest-name', 'Иван Тест')
    await page.fill('#guest-email', 'ivan.test@example.com')
    await page.fill('#guest-note', 'Тестовое бронирование')
    await page.click('button[type="submit"]')

    // 7. Check confirmation page
    await expect(page).toHaveURL(new RegExp(`/book/${user.slug}/schedules/.+/done`))
    await expect(page.locator('h1')).toContainText('Почти готово')
    await expect(page.locator('text=ivan.test@example.com')).toBeVisible()
  })

  test('profile page shows 404 message for unknown slug', async ({ page }) => {
    await page.goto('/book/this-slug-does-not-exist-ever')
    await expect(page.locator('text=не найден')).toBeVisible({ timeout: 5000 })
  })

  test('token confirm route: confirmed booking shown', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    const tomorrow = getTomorrowISO()

    // Fetch a slot via API
    const slotsRes = await request.get(
      `${API_URL}/public/${user.slug}/schedules/${schedule.id}/slots?date=${tomorrow}`,
    )
    const slots = await slotsRes.json()
    expect(slots.length).toBeGreaterThan(0)

    // Create booking via API
    const bookingRes = await request.post(
      `${API_URL}/public/${user.slug}/schedules/${schedule.id}/bookings`,
      {
        data: {
          slotId: slots[0].id,
          guestName: 'Test Guest',
          guestEmail: 'tguest@example.com',
        },
      },
    )
    const booking = await bookingRes.json()

    // Visit confirm route
    await page.goto(`/bookings/confirm/${booking.confirmationToken}`)
    await expect(page.locator('h1')).toContainText('подтверждена', { timeout: 5000 })
  })

  test('token cancel route: cancelled booking shown', async ({ page, request }) => {
    const user = await createUser(request)
    const schedule = await createSchedule(request, user.token)
    const tomorrow = getTomorrowISO()

    const slotsRes = await request.get(
      `${API_URL}/public/${user.slug}/schedules/${schedule.id}/slots?date=${tomorrow}`,
    )
    const slots = await slotsRes.json()

    const bookingRes = await request.post(
      `${API_URL}/public/${user.slug}/schedules/${schedule.id}/bookings`,
      {
        data: {
          slotId: slots[0].id,
          guestName: 'Cancel Guest',
          guestEmail: 'cguest@example.com',
        },
      },
    )
    const booking = await bookingRes.json()

    await page.goto(`/bookings/cancel/${booking.cancelToken}`)
    await expect(page.locator('h1')).toContainText('отменена', { timeout: 5000 })
  })
})
