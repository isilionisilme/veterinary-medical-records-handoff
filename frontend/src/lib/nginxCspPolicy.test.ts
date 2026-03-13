import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

function extractContentSecurityPolicy(configText: string): string {
  const match = configText.match(/Content-Security-Policy\s+"([^"]+)"/);
  if (!match) {
    throw new Error("Content-Security-Policy header not found in nginx.conf");
  }
  return match[1];
}

describe("nginx CSP policy", () => {
  it("keeps secure PDF runtime directives without unsafe-eval", () => {
    const nginxConfig = readFileSync(resolve(process.cwd(), "nginx.conf"), "utf-8");
    const csp = extractContentSecurityPolicy(nginxConfig);

    expect(csp).toContain("script-src 'self' blob:");
    expect(csp).toContain("connect-src 'self' blob:");
    expect(csp).toContain("worker-src 'self' blob:");
    expect(csp).not.toContain("'unsafe-eval'");
  });
});
