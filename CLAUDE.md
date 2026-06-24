# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Two independent, zero-dependency implementations of the same Pomodoro focus timer:

- **`focus-timer/`** — a terminal (CLI) version in Python.
- **`focus-web/`** — a browser version themed as the "Pomodoro Pizzeria" (cartoony pizza parlor).

They share no code; `focus-web` is a re-skinned port of the logic in `focus-timer/focus_timer.py`. When changing timer behavior (phase model, defaults, bell), keep the two in sync deliberately — there is no shared module.

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

There is no build step, no package manager, and no test suite.

## Architecture notes

**`focus-web/index.html` is intentionally a single self-contained file** — all CSS (`<style>`) and JS (`<script>`) are inlined, with zero external assets. This is deliberate: preview panels serve `index.html` from varying roots, so relative `style.css`/`app.js` links 404 and render the page unstyled. Do **not** re-split into separate `.css`/`.js` files. Earlier `focus-web/style.css` and `focus-web/app.js` were removed for this reason.

**Timer state machine** (both versions): a `focus` phase auto-advances to a `break`, then back to `focus`, looping. In the web version every 4th completed focus round (`LONG_BREAK_EVERY = 4`) yields a longer `longbreak` ("Wood-fired rest") instead of a normal break. The web phases carry pizza-parlor copy: `focus` = "Baking", `break` = "Cooling on the rack", `longbreak` = "Wood-fired rest".

**Web timing** is wall-clock based: `completePhase()`/`tick()` compute remaining time from `endsAt` (a `Date.now()` target), not by decrementing a counter — so it stays accurate even if interval callbacks are throttled. The tomato mascot and steam are pure inline SVG/CSS.

## Verifying changes

Changes to `focus-web` are visual; verify by reloading the preview and screenshotting. To exercise the every-4 long-break rule without waiting, the timer functions (`reset`, `completePhase`, `state`) are global in the page, so you can fast-forward via `preview_eval`. The bottom "How to Use" button toggles a collapsible instructions card.
