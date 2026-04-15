# Learn Chess Alex

Interactive chess opening study course builder powered by Stockfish engine analysis.

## What It Does

Given any chess opening system (London, Caro-Kann, Sicilian, King's Indian, etc.), this skill builds a complete interactive HTML-based study course with:

- **Animated chess board** with scroll-through move replay
- **Intent arrows** showing attack/defense/control/plan for every move
- **Stockfish branch explorer** — top 5 candidate moves per position with 6-ply continuations
- **Subtle mistake detection** — not obvious blunders, but the tricky inaccuracies that actually cost games
- **Opponent response analysis** — what they'll likely play + your best counter
- **Shape guide** — ideal piece placement, development order, strategic checklist

## Structure

```
SKILL.md                        # Skill definition (8-phase pipeline)
scripts/
  analyze_opening.py            # Stockfish 4-layer analysis engine
  verify_moves.py               # Move legality checker
references/
  html-template-guide.md        # HTML/CSS/JS architecture reference
examples/
  london-system/                # Complete London System course (demo)
    london-system-interactive.html
    london-shape.html
```

## Requirements

- Python 3.8+
- `python-chess` library (`pip install python-chess`)
- Stockfish binary (download from [stockfishchess.org](https://stockfishchess.org/download/))

## Usage

This is a Claude skill (`.skill`). Install it in Claude Code or Cowork, then say:

> "I want to learn the Caro-Kann Defense"

Claude will automatically research the opening, build variations, run Stockfish analysis, and generate the interactive course.

## License

MIT
