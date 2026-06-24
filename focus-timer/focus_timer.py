#!/usr/bin/env python3
"""Focus Timer — a terminal Pomodoro timer with live countdown and session tracking.

Usage:
    python3 focus_timer.py                 # 25m focus / 5m break, loops forever
    python3 focus_timer.py -f 50 -b 10     # custom focus/break minutes
    python3 focus_timer.py -r 4            # stop after 4 focus rounds
"""

import argparse
import sys
import time
from datetime import datetime

# ANSI colors / control codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_LINE = "\033[2K\r"

BAR_WIDTH = 30


def bell():
    """Audible terminal bell — your 'session done' nudge."""
    sys.stdout.write("\a")
    sys.stdout.flush()


def progress_bar(elapsed, total, color):
    filled = int(BAR_WIDTH * elapsed / total) if total else BAR_WIDTH
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    return f"{color}{bar}{RESET}"


def countdown(label, minutes, color):
    """Run a single phase, drawing a live one-line countdown."""
    total = int(minutes * 60)
    start = time.monotonic()
    try:
        while True:
            elapsed = time.monotonic() - start
            remaining = total - elapsed
            if remaining <= 0:
                break
            mins, secs = divmod(int(remaining + 0.999), 60)
            bar = progress_bar(elapsed, total, color)
            sys.stdout.write(
                f"{CLEAR_LINE}{color}{BOLD}{label}{RESET}  {bar}  "
                f"{BOLD}{mins:02d}:{secs:02d}{RESET}"
            )
            sys.stdout.flush()
            time.sleep(0.25)
        # final full-bar frame
        sys.stdout.write(
            f"{CLEAR_LINE}{color}{BOLD}{label}{RESET}  "
            f"{progress_bar(1, 1, color)}  {BOLD}00:00{RESET}\n"
        )
        sys.stdout.flush()
    except KeyboardInterrupt:
        elapsed_min = (time.monotonic() - start) / 60
        sys.stdout.write(f"{CLEAR_LINE}{DIM}{label} interrupted "
                         f"({elapsed_min:.1f} min in){RESET}\n")
        raise


def fmt_minutes(total_min):
    h, m = divmod(int(round(total_min)), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def main():
    p = argparse.ArgumentParser(description="A terminal Pomodoro focus timer.")
    p.add_argument("-f", "--focus", type=float, default=25, help="Focus minutes (default 25)")
    p.add_argument("-b", "--break", type=float, default=5, dest="brk", help="Break minutes (default 5)")
    p.add_argument("-r", "--rounds", type=int, default=0, help="Stop after N focus rounds (0 = forever)")
    args = p.parse_args()

    completed = 0
    focus_minutes = 0.0
    started_at = datetime.now()

    sys.stdout.write(HIDE_CURSOR)
    print(f"\n{BOLD}{MAGENTA}🍅 Focus Timer{RESET}  "
          f"{DIM}focus {args.focus:g}m · break {args.brk:g}m"
          f"{' · ' + str(args.rounds) + ' rounds' if args.rounds else ' · ∞'}{RESET}")
    print(f"{DIM}Ctrl-C anytime to stop and see your stats.{RESET}\n")

    try:
        while True:
            round_no = completed + 1
            countdown(f"FOCUS #{round_no}", args.focus, CYAN)
            completed += 1
            focus_minutes += args.focus
            bell()
            print(f"{GREEN}✓ Round {completed} done!{RESET}  "
                  f"{DIM}total focus: {fmt_minutes(focus_minutes)}{RESET}\n")

            if args.rounds and completed >= args.rounds:
                break

            countdown("BREAK   ", args.brk, YELLOW)
            bell()
            print(f"{MAGENTA}↻ Break over — back to it.{RESET}\n")
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)

    elapsed = (datetime.now() - started_at)
    mins = elapsed.total_seconds() / 60
    print(f"\n{BOLD}── Session summary ──{RESET}")
    print(f"  Focus rounds completed : {BOLD}{completed}{RESET}")
    print(f"  Time focused           : {BOLD}{fmt_minutes(focus_minutes)}{RESET}")
    print(f"  Total elapsed          : {fmt_minutes(mins)}")
    print(f"{GREEN}Nice work.{RESET}\n")


if __name__ == "__main__":
    main()
