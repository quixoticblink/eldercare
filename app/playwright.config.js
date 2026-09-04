// Kakis end-to-end tests. One worker: the backend is a single DuckDB file
// under one lock, and every spec shares the same throwaway database that
// run-server.sh recreates at startup. Phone-sized viewport — the app is
// phone-first and seniors used their own phones on 21 Aug.
const { defineConfig, devices } = require("@playwright/test");

const PORT = 8100;

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: { timeout: 7_000 },
  workers: 1,
  fullyParallel: false,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    viewport: { width: 390, height: 844 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 390, height: 844 } } }],
  webServer: {
    command: "bash tests/e2e/run-server.sh",
    url: `http://127.0.0.1:${PORT}/api/health`,
    reuseExistingServer: false,
    timeout: 60_000,
    stdout: "pipe",
    stderr: "pipe",
  },
});
