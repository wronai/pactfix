import { defineConfig, devices } from '@playwright/test';

const port = process.env.PLAYWRIGHT_PORT || process.env.PORT || '8099';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: `http://localhost:${port}`,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'python3 server.py',
    url: `http://localhost:${port}`,
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
    env: {
      APP_DIR: './app',
      PORT: port,
    },
  },
});
