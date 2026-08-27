import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("home is accessible and the CSV demo works", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  await page.goto("/");
  await expect(page).toHaveTitle(/tabular-file-diff/);
  await expect(page.locator("main")).toHaveCount(1);
  await expect(page.locator("h1")).toHaveCount(1);
  await expect(page.getByRole("img")).toHaveJSProperty("complete", true);

  await page.getByRole("button", { name: "Load sample" }).click();
  await page.getByRole("button", { name: "Compare rows" }).click();
  await expect(page.locator("#added-count")).toHaveText("1");
  await expect(page.locator("#removed-count")).toHaveText("1");
  await expect(page.locator("#modified-count")).toHaveText("2");
  await expect(page.locator("#demo-status")).toContainText("Comparison complete");

  await page.getByRole("tab", { name: "DVC" }).click();
  await expect(page.getByRole("tabpanel", { name: "DVC" })).toBeVisible();
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
  expect(errors).toEqual([]);

  if (testInfo.project.name === "mobile") {
    const widths = await page.evaluate(() => ({
      document: document.documentElement.scrollWidth,
      window: window.innerWidth
    }));
    expect(widths.document).toBeLessThanOrEqual(widths.window);
    await page.screenshot({ path: testInfo.outputPath("home-mobile.png"), fullPage: true });
  }
});

for (const path of ["/privacy/", "/terms/"]) {
  test(`${path} has no serious accessibility violations`, async ({ page }) => {
    await page.goto(path);
    await expect(page.locator("main")).toHaveCount(1);
    await expect(page.locator("h1")).toHaveCount(1);
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}
