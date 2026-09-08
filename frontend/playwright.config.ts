import { defineConfig } from '@playwright/test'

const apiUrl = process.env.VITE_API_URL ?? 'http://localhost:8000'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    env: {
      VITE_API_URL: apiUrl,
    },
  },
})
