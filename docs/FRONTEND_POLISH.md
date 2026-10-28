# Frontend playback stability and polish — 28 October 2026

The Match Centre now retains the last confirmed score and clock during forward
playback requests and labels their confirmed state. Fixed score columns, tabular
numerals and reserved control widths prevent loading text, changing digits and
Play/Pause labels from moving the fixture or playback controls. Backward seeks
hide later scores and forecasts until eligible data arrives; changing fixtures
still clears the snapshots. Forecast refreshes retain their labeled previous
result, and chart updates no longer restart entrance animations.

Visual changes preserve all four workspaces, navigation, content and palette:
subtle background shading, restrained panel shadows, clearer pitch markings and
shot outlines, active navigation treatment and hover/focus states. Disabled
buttons no longer receive enabled hover treatment. No backend or infrastructure
files changed.

Verification against the production frontend served by the existing local API:

- `npm run build --prefix frontend`: passes TypeScript and Vite production build.
  The existing bundle-size advisory remains (approximately 538 kB minified JS).
- `CHROMIUM_PATH=/usr/bin/chromium BASE_URL=http://127.0.0.1:8010 npm run test:e2e --prefix frontend`:
  **6 passed in 15.0 seconds**: four existing journeys plus two delayed-response regression cases at 1280 px
  and 390 px. The regression cases verify unchanged scoreboard geometry and team
  positions during playback, retained forecast values, backwards-seek protection
  and no horizontal overflow.
- Desktop and mobile screenshots in `docs/screenshots/` refreshed and inspected.

Browser tests use the existing deterministic development mode and a temporary
SQLite database; they do not require Foundry calls or Azure resources.
