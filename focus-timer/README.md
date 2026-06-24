# 🍅 Focus Timer

A zero-dependency terminal Pomodoro timer with a live countdown, progress bar, and session stats.

## Run

```bash
python3 focus_timer.py                 # 25m focus / 5m break, loops forever
python3 focus_timer.py -f 50 -b 10     # custom focus/break minutes
python3 focus_timer.py -r 4            # stop after 4 focus rounds
```

Press **Ctrl-C** anytime to stop and see your session summary.

## Options

| Flag | Meaning | Default |
|------|---------|---------|
| `-f, --focus`  | Focus minutes | 25 |
| `-b, --break`  | Break minutes | 5  |
| `-r, --rounds` | Stop after N focus rounds (0 = forever) | 0 |

A terminal bell rings at the end of each focus and break phase.
