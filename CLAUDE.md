# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Two independent, zero-dependency implementations of the same Pomodoro focus timer:

- **`focus-timer/`** — a terminal (CLI) version in Python.
- **`focus-web/`** — a browser version themed as the "Pomodoro Pizzeria" (cartoony pizza parlor).

They share no code; `focus-web` is a re-skinned port of the logic in `focus-timer/focus_timer.py`. When changing timer behavior (phase model, defaults, bell), keep the two in sync deliberately — there is no shared module.

A third, unrelated app also lives here:

- **`jp-pricing/`** — the "JP Pricing Tool", a single-file browser app themed as a realistic Japanese bamboo forest. It uploads Japanese MHLW drug-price publication PDFs, sends each to Claude (`claude-opus-4-8`) **directly from the browser**, and renders an English-translated summary table of pricing details (pricing method, premiums/補正加算, foreign price adjustment, PMP eligibility, etc.) with expandable per-drug detail and an Excel (`.xlsx`) export. It shares no code with the timers.

## Running

Terminal version:
```bash
python3 focus-timer/focus_timer.py            # 25m focus / 5m break, loops forever
python3 focus-timer/focus_timer.py -f 50 -b 10 -r 4   # custom focus/break minutes, stop after 4 rounds
```

Web version — served as static files via Python's stdlib HTTP server, configured in `.claude/launch.json` (name `focus-web`, port **5501**):
```bash
python3 -m http.server 5501 --directory focus-web
```
Prefer the preview tooling (`preview_start` with the `focus-web` config) over launching the server manually.

JP Pricing Tool — also static, configured in `.claude/launch.json` (name `jp-pricing`, port **5502**):
```bash
python3 -m http.server 5502 --directory jp-pricing
```

There is no build step, no package manager, and no test suite.

## Deployment

The repo is on GitHub (`mattlyons102/pomodoro-pizzeria`, public) and deploys to
Vercel as a static site. Because the apps live in subfolders rather than the repo
root, the root `vercel.json` has two rewrites: `/` → `/focus-web/index.html` and
`/jp-pricing` → `/jp-pricing/index.html` (each works because the page is a single
self-contained file). Keep Vercel's **Root Directory** at the default — do not
point it at a subfolder, or it will conflict with the rewrites. Pushing to `main`
triggers an auto-deploy. The JP Pricing Tool is therefore reachable at
`<deployment>/jp-pricing`; each visitor supplies their own Anthropic API key
(stored in their own browser), so no key is ever committed.

## Architecture notes

**`focus-web/index.html` is intentionally a single self-contained file** — all CSS (`<style>`) and JS (`<script>`) are inlined, with zero external assets. This is deliberate: preview panels serve `index.html` from varying roots, so relative `style.css`/`app.js` links 404 and render the page unstyled. Do **not** re-split into separate `.css`/`.js` files. Earlier `focus-web/style.css` and `focus-web/app.js` were removed for this reason.

**Timer state machine** (both versions): a `focus` phase auto-advances to a `break`, then back to `focus`, looping. In the web version every 4th completed focus round (`LONG_BREAK_EVERY = 4`) yields a longer `longbreak` ("Wood-fired rest") instead of a normal break. The web phases carry pizza-parlor copy: `focus` = "Baking", `break` = "Cooling on the rack", `longbreak` = "Wood-fired rest".

**Web timing** is wall-clock based: `completePhase()`/`tick()` compute remaining time from `endsAt` (a `Date.now()` target), not by decrementing a counter — so it stays accurate even if interval callbacks are throttled. The tomato mascot and steam are pure inline SVG/CSS.

**`jp-pricing/index.html`** follows the same single-self-contained-file rule, with **one deliberate exception**: SheetJS for `.xlsx` export is loaded from an absolute CDN URL. An absolute URL is immune to the relative-path 404 problem (which is why inlining everything else still matters), and the page degrades gracefully if the CDN is blocked (only export is affected). The page calls the Anthropic Messages API directly via `fetch` with the `anthropic-dangerous-direct-browser-access: true` header; PDFs go up as base64 `document` blocks and extraction uses `output_config.format` (structured JSON output), so there is no separate OCR/pdf.js layer. The bamboo forest, komorebi light shafts, and dust motes are pure CSS plus a JS-drawn inline `<svg>`. The API key lives only in `localStorage` (`jp_pricing_api_key`). The "Load sample row" button seeds a demo drug so the table, expandable detail, and Excel export can be exercised without an API key.

## Verifying changes

Changes to `focus-web` are visual; verify by reloading the preview and screenshotting. To exercise the every-4 long-break rule without waiting, the timer functions (`reset`, `completePhase`, `state`) are global in the page, so you can fast-forward via `preview_eval`. The bottom "How to Use" button toggles a collapsible instructions card.

For `jp-pricing`, use the "Load sample row" button (or `els.sampleBtn.click()` via `preview_eval`) to populate results without a key, then verify the table, the expandable drop-down detail, and the `.xlsx` export. Real extraction needs a valid Anthropic API key and a real MHLW PDF.
