import { test, expect } from '@playwright/test'

test('renders the home route', async ({ page }) => {
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Project8 DS2' }),
  ).toBeVisible()
})

test('renders the shadcn button', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('button', { name: 'Click me' })).toBeVisible()
})

test('exposes the configured VITE_API_URL', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByTestId('api-url')).toHaveText(
    process.env.VITE_API_URL ?? 'http://localhost:8000',
  )
})
