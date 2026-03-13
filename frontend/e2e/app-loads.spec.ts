import { expect, test } from "@playwright/test";

test("app loads main layout", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
  await expect(page.getByTestId("upload-dropzone").first()).toBeVisible();
  const emptyState = page.getByTestId("viewer-empty-state");
  await expect(emptyState).toBeVisible();
  await expect(emptyState).toContainText("Selecciona un documento");
});
