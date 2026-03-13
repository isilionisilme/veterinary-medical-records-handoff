import AxeBuilder from "@axe-core/playwright";

import { expect, test } from "./fixtures";
import { selectDocument, uploadAndWaitForProcessing } from "./helpers";

function getCriticalViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  return results.violations.filter((violation) => violation.impact === "critical");
}

function getSeriousAndCriticalViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  return results.violations.filter(
    (violation) => violation.impact === "critical" || violation.impact === "serious",
  );
}

test.describe("Accessibility — WCAG 2.1 AA", () => {
  test("upload view has no critical violations", async ({ page }) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(getCriticalViolations(results)).toEqual([]);
  });

  test("review view has no critical violations", async ({ page }) => {
    await page.goto("/");
    const documentId = await uploadAndWaitForProcessing(page, "e2e/fixtures/sample.pdf", {
      timeout: 90_000,
    });
    await selectDocument(page, documentId);

    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(getCriticalViolations(results)).toEqual([]);
  });

  test("full app audit keeps serious+critical violations under threshold", async ({ page }) => {
    await page.goto("/");
    const documentId = await uploadAndWaitForProcessing(page, "e2e/fixtures/sample.pdf", {
      timeout: 90_000,
    });
    await selectDocument(page, documentId);

    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    const seriousViolations = getSeriousAndCriticalViolations(results);

    if (seriousViolations.length > 0) {
      console.log("Serious accessibility violations:", JSON.stringify(seriousViolations, null, 2));
    }

    expect(seriousViolations.length).toBeLessThan(5);
  });
});
