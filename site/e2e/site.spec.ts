import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

async function expectDemo(page: import("@playwright/test").Page): Promise<void> {
  await expect(page.getByText("Demo — sample data, nothing is saved")).toBeVisible();
  await expect(page.locator("#added-count")).toHaveText("1");
  await expect(page.locator("#removed-count")).toHaveText("1");
  await expect(page.locator("#modified-count")).toHaveText("2");
  await expect(page.getByText("Added: region")).toBeVisible();
  await expect(page.locator("#change-table")).toBeVisible();
  await expect(page.locator("#proof-columns")).toHaveText(/^(status 1 · amount 1|amount 1 · status 1)$/);
  await expect(page.locator("#proof-schema")).toHaveText("region added");
  await expect(page.locator("#proof-row")).toContainText("A-101 · status: open → closed");
}

test("@claim:demo-one-click direct demo shows the shipped comparison", async ({ page }) => {
  await page.goto("/?demo=1");
  await expect(page).toHaveURL(/\/demo\/$/);
  await expectDemo(page);
  await expect(page).toHaveTitle("Demo — tdiff");
  const proof = await page.locator("#demo-result").boundingBox();
  const viewport = page.viewportSize();
  expect(proof).not.toBeNull();
  expect(viewport).not.toBeNull();
  expect(proof!.y).toBeGreaterThanOrEqual(0);
  expect(proof!.y + proof!.height).toBeLessThanOrEqual(viewport!.height);
  await page.goto("/demo/");
  await expectDemo(page);
});

test("@claim:demo-isolation reset restores sample and start-for-real clears demo storage", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => sessionStorage.setItem("real:keep", "visitor-data"));
  await page.goto("/demo/");
  await expect(page.evaluate(() => Object.keys(sessionStorage).sort())).resolves.toEqual(["demo:sample-comparison", "real:keep"]);
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expectDemo(page);
  await page.getByRole("link", { name: "Start for real" }).click();
  await expect(page).toHaveURL("/");
  await expect(page.evaluate(() => Object.fromEntries(Object.entries(sessionStorage)))).resolves.toEqual({ "real:keep": "visitor-data" });
});

test("@claim:browser-private demo sends no request beyond this origin", async ({ page }) => {
  const requests: { origin: string; method: string }[] = [];
  page.on("request", (request) => requests.push({ origin: new URL(request.url()).origin, method: request.method() }));
  await page.goto("/demo/");
  await expectDemo(page);
  await page.locator("#old-file").setInputFiles({ name: "private-old.csv", mimeType: "text/csv", buffer: Buffer.from("id,value\n1,old\n2,removed\n") });
  await page.locator("#new-file").setInputFiles({ name: "private-new.csv", mimeType: "text/csv", buffer: Buffer.from("id,value\n1,new\n3,added\n") });
  await page.getByRole("button", { name: "Compare rows" }).click();
  await expect(page.locator("#modified-count")).toHaveText("1");
  expect(new Set(requests.map((request) => request.origin))).toEqual(new Set(["http://127.0.0.1:4173"]));
  expect(requests.every((request) => request.method === "GET")).toBe(true);
  expect(await page.context().cookies()).toEqual([]);
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
});

test("@claim:browser-csv selected CSV files are compared in this tab", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  await page.goto("/demo/");
  const loadedRequests = requests.length;
  await page.locator("#old-file").setInputFiles({ name: "old.csv", mimeType: "text/csv", buffer: Buffer.from("id,value\n1,old\n2,same\n") });
  await page.locator("#new-file").setInputFiles({ name: "new.csv", mimeType: "text/csv", buffer: Buffer.from("id,value\n1,new\n3,added\n") });
  await page.getByRole("button", { name: "Compare rows" }).click();
  await expect(page.locator("#added-count")).toHaveText("1");
  await expect(page.locator("#removed-count")).toHaveText("1");
  await expect(page.locator("#modified-count")).toHaveText("1");
  expect(requests).toHaveLength(loadedRequests);
  await expect(page.locator("#old-file")).toHaveAttribute("accept", ".csv,text/csv");
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
    const heading = await page.locator("h1").boundingBox();
    expect(heading).not.toBeNull();
    expect(heading!.x + heading!.width).toBeLessThanOrEqual(390);
  }
});

for (const route of [
  { path: "/demo/", title: "Demo — tdiff" },
  { path: "/privacy/", title: "Privacy — tdiff" },
  { path: "/terms/", title: "Terms — tdiff" }
]) {
  test(route.path + " has complete metadata, one heading, and no accessibility violations", async ({ page }) => {
    await page.goto(route.path);
    await expect(page).toHaveTitle(route.title);
    await expect(page.locator("main")).toHaveCount(1);
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.locator("h1")).toBeFocused();
    await expect(page.locator("#route-announcer")).not.toBeEmpty();
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", `https://tabular-file-diff.sociobot.in${route.path}`);
    await expect(page.locator('meta[property="og:title"]')).toHaveAttribute("content", route.title);
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute("content", /og-image\.png$/);
    await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute("content", "summary_large_image");
    await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute("href", "/apple-touch-icon.png");
    await expect(page.locator('footer a[href="/privacy/"]')).toBeVisible();
    await expect(page.locator('footer a[href="/terms/"]')).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
}

test("legal navigation, history, and the 404 route preserve metadata and focus", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Privacy", exact: true }).first().click();
  await expect(page).toHaveURL(/\/privacy\/$/);
  await expect(page.locator("h1")).toBeFocused();
  await expect(page).toHaveTitle("Privacy — tdiff");
  await page.goBack();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.locator("h1")).toBeFocused();

  await page.goto("/terms/");
  await expect(page.locator("h1")).toBeFocused();
  await expect(page).toHaveTitle("Terms — tdiff");

  const response = await page.goto("/does-not-exist");
  expect(response?.status()).toBe(404);
  await expect(page).toHaveTitle("Route not found — tdiff");
  await expect(page.locator("h1")).toBeFocused();
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://tabular-file-diff.sociobot.in/404.html");
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute("content", /og-image\.png$/);
  await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute("content", "summary_large_image");
  await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute("href", "/apple-touch-icon.png");
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  expect(results.violations).toEqual([]);
});
