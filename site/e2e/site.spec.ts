import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

async function expectDemo(page: import("@playwright/test").Page): Promise<void> {
  await expect(page.getByText("Demo — sample data, nothing is saved")).toBeVisible();
  await expect(page.locator("#added-count")).toHaveText("1");
  await expect(page.locator("#removed-count")).toHaveText("1");
  await expect(page.locator("#modified-count")).toHaveText("2");
  await expect(page.getByText("Added: region")).toBeVisible();
  await expect(page.locator("#change-table")).toBeVisible();
}

test("@claim:demo-one-click direct demo shows the shipped comparison", async ({ page }) => {
  await page.goto("/?demo=1");
  await expect(page).toHaveURL(/\/demo\/$/);
  await expectDemo(page);
  await expect(page).toHaveTitle("Demo — tdiff");
  await page.goto("/demo/");
  await expectDemo(page);
});

test("@claim:demo-isolation reset restores sample and start-for-real clears demo storage", async ({ page }) => {
  await page.goto("/demo/");
  await expect(page.evaluate(() => Object.keys(sessionStorage))).resolves.toEqual(["demo:sample-comparison"]);
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expectDemo(page);
  await page.getByRole("link", { name: "Start for real" }).click();
  await expect(page).toHaveURL("/");
  await expect(page.evaluate(() => Object.keys(sessionStorage))).resolves.toEqual([]);
});

test("@claim:browser-private demo sends no request beyond this origin", async ({ page }) => {
  const requests: { origin: string; method: string }[] = [];
  page.on("request", (request) => requests.push({ origin: new URL(request.url()).origin, method: request.method() }));
  await page.goto("/demo/");
  await expectDemo(page);
  expect(new Set(requests.map((request) => request.origin))).toEqual(new Set(["http://127.0.0.1:4173"]));
  expect(requests.every((request) => request.method === "GET")).toBe(true);
});

test("@claim:no-account demo opens without an account form", async ({ page }) => {
  await page.goto("/demo/");
  await expectDemo(page);
  await expect(page.locator('input[type="password"], input[name*="email" i], form[action*="login" i]')).toHaveCount(0);
});

test("@claim:offline-demo demo reloads after its first visit", async ({ context, page }) => {
  await page.goto("/demo/");
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expectDemo(page);
  await context.setOffline(true);
  await page.reload();
  await expectDemo(page);
});

test("home, routes, keyboard controls, and mobile layout are accessible", async ({ context, page }, testInfo) => {
  const errors: string[] = [];
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto("/");
  await expect(page).toHaveTitle("tdiff — Compare keyed data files");
  await expect(page.locator("main")).toHaveCount(1);
  await expect(page.locator("h1")).toHaveCount(1);
  await expect(page.getByRole("link", { name: "Try it with sample data" })).toHaveAttribute("href", "/demo/");

  await page.getByRole("tab", { name: "DVC" }).click();
  await expect(page.getByRole("tabpanel", { name: "DVC" })).toBeVisible();
  await page.getByRole("tab", { name: "DVC" }).press("ArrowLeft");
  await expect(page.getByRole("tabpanel", { name: "Git" })).toBeVisible();
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(results.violations).toEqual([]);
  expect(errors).toEqual([]);

  await context.setOffline(true);
  await expect(page.locator("#offline-notice")).toBeVisible();
  await context.setOffline(false);
  if (testInfo.project.name === "mobile") {
    const widths = await page.evaluate(() => ({ document: document.documentElement.scrollWidth, window: window.innerWidth }));
    expect(widths.document).toBeLessThanOrEqual(widths.window);
  }
});

for (const path of ["/demo/", "/privacy/", "/terms/"]) {
  test(path + " has one main heading and no serious accessibility violations", async ({ page }) => {
    await page.goto(path);
    await expect(page.locator("main")).toHaveCount(1);
    await expect(page.locator("h1")).toHaveCount(1);
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
}
