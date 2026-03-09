import { defineConfig } from "@playwright/test";
import os from "node:os";

const useExternalServers = process.env.PLAYWRIGHT_EXTERNAL_SERVERS === "1";
const defaultBackendPort = process.env.CI || useExternalServers ? 8000 : 18000;
const defaultFrontendPort = process.env.CI || useExternalServers ? 5173 : 15173;
const cpuCount = os.cpus().length;
const maxWorkers = Math.max(1, cpuCount);

function resolvePort(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function resolveWorkerCount(value: string | undefined): number | undefined {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined;
}

const backendPort = resolvePort(process.env.PLAYWRIGHT_BACKEND_PORT, defaultBackendPort);
const frontendPort = resolvePort(process.env.PLAYWRIGHT_FRONTEND_PORT, defaultFrontendPort);
const backendBaseURL = process.env.PLAYWRIGHT_BACKEND_BASE_URL || `http://127.0.0.1:${backendPort}`;
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`;
// Keep local runs fast by default, but avoid oversaturating the machine.
const localDefaultWorkers = Math.min(12, maxWorkers, Math.max(1, Math.floor(cpuCount * 0.75)));
const ciDefaultWorkers = Math.min(maxWorkers, 6);
const requestedWorkers = resolveWorkerCount(process.env.PLAYWRIGHT_WORKERS)
  ?? (process.env.CI
    ? resolveWorkerCount(process.env.PLAYWRIGHT_CI_WORKERS) ?? ciDefaultWorkers
    : localDefaultWorkers);
const workers = Math.min(maxWorkers, requestedWorkers);
const webServer = useExternalServers
  ? undefined
  : [
      {
        command:
          `python -m uvicorn backend.app.main:create_app --factory --host 127.0.0.1 --port ${backendPort}`,
        url: `${backendBaseURL}/openapi.json`,
        cwd: "..",
        // Backend may already be running (local or CI docker stack).
        reuseExistingServer: true,
        timeout: 120_000,
      },
      {
        command: `node ./node_modules/vite/bin/vite.js --host 127.0.0.1 --port ${frontendPort}`,
        url: baseURL,
        cwd: ".",
        env: {
          ...process.env,
          VITE_API_BASE_URL: backendBaseURL,
        },
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
    ];

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  workers,
  expect: {
    timeout: 5_000,
  },
  outputDir: "./test-results",
  // Stabilize CI against intermittent timing/network-related flakes.
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL,
    headless: true,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "smoke",
      testMatch: /app-loads|upload-smoke/,
      timeout: 30_000,
    },
    {
      name: "core",
      testMatch: /pdf-viewer|extracted-data|field-editing|review-workflow|document-sidebar/,
      timeout: 60_000,
    },
    {
      name: "extended",
      testMatch: /.*\.spec\.ts$/,
      timeout: 90_000,
    },
  ],
  webServer,
  reporter: [["html", { outputFolder: "playwright-report", open: "never" }]],
});
