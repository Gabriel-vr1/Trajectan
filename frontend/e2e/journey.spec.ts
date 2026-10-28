import { test, expect } from "@playwright/test";

test("complete intelligence journey with immutable scenario and personalized recap", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Play match" })).toBeEnabled();
  await page.getByRole("button", { name: "Half-time", exact: true }).click();
  await expect(
    page.getByText("HISTORICAL MOMENT", { exact: false }),
  ).toBeVisible();
  await expect(page.getByText("45:00 · HALF 1")).toBeVisible();
  await page.getByRole("button", { name: "Investigate this moment" }).click();
  await expect(
    page.getByText("deterministic-development-fallback", { exact: true }),
  ).toBeVisible({ timeout: 45000 });
  await expect(
    page.getByRole("heading", { name: /State \d+ · published/ }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Scenario Lab", exact: false })
    .click();
  await page.getByRole("button", { name: "Run paired simulation" }).click();
  await expect(
    page.getByRole("heading", { name: "With intervention" }),
  ).toBeVisible({ timeout: 30000 });
  await expect(page.getByText("45:00 · HALF 1")).toBeVisible();
  await page
    .getByRole("button", { name: "Broadcast & Recaps", exact: false })
    .click();
  await expect(
    page.getByRole("button", { name: "Export verified overlay" }),
  ).toBeEnabled();
  const viewer = await page.locator(".broadcast-body p").innerText();
  await page.getByLabel("Audience mode").selectOption("analyst");
  await expect(page.locator(".broadcast-body p")).toContainText(
    "Monte Carlo SE",
  );
  expect(await page.locator(".broadcast-body p").innerText()).not.toEqual(
    viewer,
  );
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export verified overlay" }).click();
  expect((await download).suggestedFilename()).toContain("analyst.json");
  await page.screenshot({
    path: "../docs/screenshots/broadcast-desktop.png",
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Match Centre", exact: false })
    .click();
  await page.screenshot({
    path: "../docs/screenshots/match-desktop.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});

test("playback, historical cursor, fixture reset and responsive layout", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Play match" }).click();
  await expect(page.getByText(/PLAYBACK HEAD · STATE [1-9]/)).toBeVisible();
  await page.getByRole("button", { name: "Pause" }).click();
  await page.getByRole("button", { name: "Full-time", exact: true }).click();
  await expect(page.getByText("90:00 · FULL TIME")).toBeVisible();
  await page
    .getByRole("button", { name: "Scenario Lab", exact: false })
    .click();
  await expect(
    page.getByRole("button", { name: "Run paired simulation" }),
  ).toBeDisabled();
  await page.getByLabel("Seeded fixture").selectOption("77");
  await expect(page.getByText("PLAYBACK HEAD · STATE 0")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page
    .getByRole("button", { name: "Match Centre", exact: false })
    .click();
  await page.screenshot({
    path: "../docs/screenshots/match-mobile.png",
    fullPage: true,
  });
});

test("attribution intervals and alternate factor order remain reconciled", async ({
  page,
}) => {
  // Reproduce cold/remote fixture loading: seeking before events arrive used
  // to select state zero and leave attribution permanently disabled.
  await page.route("**/api/matches/26", async (route) => {
    const response = await route.fetch();
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.fulfill({ response });
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Half-time", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Full-time", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Half-time", exact: true }).click();
  await expect(page.getByText("45:00 · HALF 1")).toBeVisible();
  await page.getByRole("button", { name: "Explain forecast change" }).click();
  await expect(
    page.getByRole("heading", { name: "What moved the home-win forecast?" }),
  ).toBeVisible({ timeout: 30000 });
  await expect(page.locator(".factor-uncertainty")).toContainText(
    "95% interval",
  );
  await expect(page.locator(".attribution")).toContainText("Reconciled");
  await page
    .getByRole("button", { name: "Compare reverse factor order" })
    .click();
  await expect(
    page.getByRole("button", { name: "Compare forward factor order" }),
  ).toBeVisible({ timeout: 30000 });
  await expect(page.locator(".attribution")).toContainText("Reconciled");
});

test("a late scenario response cannot change a different fixture", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Half-time", exact: true }).click();
  await page
    .getByRole("button", { name: "Scenario Lab", exact: false })
    .click();
  await page.route("**/api/jobs/**", async (route) => {
    const response = await route.fetch();
    await new Promise((r) => setTimeout(r, 1000));
    await route.fulfill({ response });
  });
  await page.getByRole("button", { name: "Run paired simulation" }).click();
  await page.getByLabel("Seeded fixture").selectOption("77");
  await expect(page.getByText("PLAYBACK HEAD · STATE 0")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "With intervention" }),
  ).toHaveCount(0);
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Run paired simulation" }),
  ).toBeEnabled();
});

for (const width of [1280, 390]) {
  test(`scoreboard and forecast stay stable during delayed playback at ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    await expect(page.locator(".score-source")).toHaveText("Confirmed state 0");
    await expect(page.locator(".probabilities")).toBeVisible();
    const score = page.locator(".score");
    const before = await score.boundingBox();
    const teams = await page
      .locator(".fixture h2")
      .evaluateAll((nodes) => nodes.map((n) => n.getBoundingClientRect().x));
    const initialScore = await score.locator("strong").innerText();
    const probabilities = await page.locator(".probabilities").innerText();
    let release!: () => void;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route(
      /\/api\/matches\/26\/(states|forecasts)\/[1-9]\d*$/,
      async (route) => {
        const response = await route.fetch();
        await gate;
        await route.fulfill({ response });
      },
    );
    try {
      await page
        .getByRole("button", { name: "Play match", exact: true })
        .click();
      await expect(page.getByText(/PLAYBACK HEAD · STATE [1-9]/)).toBeVisible();
      await page.getByRole("button", { name: "Pause", exact: true }).click();
      await expect(score.locator("strong")).toHaveText(initialScore);
      await expect(score).not.toContainText("Loading");
      await expect(page.locator(".probabilities")).toHaveText(probabilities, {
        useInnerText: true,
      });
      expect(await score.boundingBox()).toEqual(before);
      expect(
        await page
          .locator(".fixture h2")
          .evaluateAll((nodes) =>
            nodes.map((n) => n.getBoundingClientRect().x),
          ),
      ).toEqual(teams);
    } finally {
      release();
    }
    await expect(page.locator(".score-source")).not.toHaveText(
      "Confirmed state 0",
    );
    await expect(page.locator(".bottom-grid > section").first()).toContainText(
      /continuations · state [1-9]/,
    );
    // A backwards seek must not reuse a later score or forecast while pending.
    let releaseZero!: () => void;
    const zeroGate = new Promise<void>((resolve) => {
      releaseZero = resolve;
    });
    await page.route(
      /\/api\/matches\/26\/(states|forecasts)\/0$/,
      async (route) => {
        const response = await route.fetch();
        await zeroGate;
        await route.fulfill({ response });
      },
    );
    try {
      await page.getByLabel("Historical match position").fill("0");
      await expect(score.locator("strong")).toHaveText("— : —");
      await expect(page.locator(".probabilities")).toHaveCount(0);
      expect(await score.boundingBox()).toEqual(before);
    } finally {
      releaseZero();
    }
    await expect(page.locator(".score-source")).toHaveText("Confirmed state 0");
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
}
