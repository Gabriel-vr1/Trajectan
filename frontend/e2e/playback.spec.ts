import { test, expect } from "@playwright/test";

declare global {
  interface Window {
    playbackConnections: EventSource[];
    maxPlaybackConnections: number;
  }
}

test.beforeEach(async ({ page }) => {
  // Observe real EventSource connections without replacing the server stream.
  await page.addInitScript(() => {
    window.playbackConnections = [];
    window.maxPlaybackConnections = 0;
    const NativeEventSource = window.EventSource;
    window.EventSource = class extends NativeEventSource {
      constructor(url: string | URL, options?: EventSourceInit) {
        super(url, options);
        window.playbackConnections.push(this);
        window.maxPlaybackConnections = Math.max(
          window.maxPlaybackConnections,
          window.playbackConnections.filter((s) => s.readyState !== 2).length,
        );
      }
    };
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Play match", exact: true }),
  ).toBeEnabled();
});

for (const target of [120, 20]) {
  test(`seeking ${target > 60 ? "forward" : "backward"} resumes from the selected position`, async ({
    page,
  }) => {
    const timeline = page.getByLabel("Historical match position");
    const play = page.getByRole("button", { name: "Play match", exact: true });
    const pause = page.getByRole("button", { name: "Pause", exact: true });
    await timeline.fill("60");
    await play.click();
    await expect
      .poll(async () => Number(await timeline.inputValue()))
      .toBeGreaterThan(60);
    // Seeking during playback must immediately close the previous connection.
    await timeline.fill(String(target));
    await expect(play).toBeVisible();
    await expect(timeline).toHaveValue(String(target));
    expect(
      await page.evaluate(() =>
        window.playbackConnections.every((s) => s.readyState === 2),
      ),
    ).toBe(true);
    await play.click();
    await expect
      .poll(() =>
        page.evaluate(() =>
          new URL(window.playbackConnections.at(-1)!.url).searchParams.get(
            "after",
          ),
        ),
      )
      .toBe(String(target));
    await expect
      .poll(async () => Number(await timeline.inputValue()))
      .toBeGreaterThan(target);
    await pause.click();
    const pausedAt = await timeline.inputValue();
    // Even an already-queued callback on a closed connection must be ignored.
    await page.evaluate(() => {
      for (const stream of window.playbackConnections) {
        stream.dispatchEvent(
          new MessageEvent("match", {
            data: JSON.stringify({ sequence: 347, kind: "fulltime" }),
          }),
        );
        stream.dispatchEvent(new Event("error"));
      }
    });
    await expect(timeline).toHaveValue(pausedAt);
    await expect(page.getByRole("alert")).toHaveCount(0);
    await play.click();
    await expect
      .poll(() =>
        page.evaluate(() =>
          new URL(window.playbackConnections.at(-1)!.url).searchParams.get(
            "after",
          ),
        ),
      )
      .toBe(pausedAt);
    await expect
      .poll(async () => Number(await timeline.inputValue()))
      .toBeGreaterThan(Number(pausedAt));
    await pause.click();
    expect(await page.evaluate(() => window.maxPlaybackConnections)).toBe(1);
    expect(await page.evaluate(() => window.playbackConnections.length)).toBe(
      3,
    );
  });
}

test("checkpoint controls and replay after full time use the selected position", async ({
  page,
}) => {
  const timeline = page.getByLabel("Historical match position");
  const play = page.getByRole("button", { name: "Play match", exact: true });
  await page.getByRole("button", { name: "Step", exact: false }).click();
  await expect(timeline).toHaveValue("1");
  await timeline.fill("50");
  await page
    .getByRole("button", { name: "Return to live", exact: true })
    .click();
  await expect(timeline).toHaveValue("1");
  await timeline.fill("50");
  await page.getByRole("button", { name: "Step", exact: false }).click();
  await expect(timeline).toHaveValue("51");
  await page.getByRole("button", { name: "Half-time", exact: true }).click();
  await expect(page.getByText("45:00 · HALF 1")).toBeVisible();
  const half = await timeline.inputValue();
  await play.click();
  await expect
    .poll(() =>
      page.evaluate(() =>
        new URL(window.playbackConnections.at(-1)!.url).searchParams.get(
          "after",
        ),
      ),
    )
    .toBe(half);
  await page.getByRole("button", { name: "Full-time", exact: true }).click();
  await expect(play).toBeDisabled();
  const end = Number(await timeline.getAttribute("max"));
  await timeline.fill(String(end - 1));
  await play.click();
  await expect(timeline).toHaveValue(String(end));
  await expect(play).toBeDisabled();
  await timeline.fill("10");
  await expect(play).toBeEnabled();
  await play.click();
  await expect
    .poll(() =>
      page.evaluate(() =>
        new URL(window.playbackConnections.at(-1)!.url).searchParams.get(
          "after",
        ),
      ),
    )
    .toBe("10");
  await expect
    .poll(async () => Number(await timeline.inputValue()))
    .toBeGreaterThan(10);
  expect(await page.evaluate(() => window.maxPlaybackConnections)).toBe(1);
});
