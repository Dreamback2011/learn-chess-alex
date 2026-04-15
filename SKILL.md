---
name: learn-chess-alex
description: >
  Build interactive chess opening study courses with Stockfish engine analysis.
  Use this skill whenever the user wants to: learn a chess opening system (London, Caro-Kann, Sicilian, King's Indian, etc.),
  analyze chess positions with engine evaluation, create chess training materials, study opening variations with move-by-move breakdowns,
  understand when to use or deviate from an opening system, or build an interactive chess study tool.
  Also trigger when the user mentions: chess openings, Stockfish analysis, opening repertoire, variation tree, chess study plan,
  opening preparation, move order, chess engine evaluation, or chess position analysis.
  This skill generates a complete interactive HTML-based course with animated chess boards, Stockfish-powered analysis,
  branch exploration, and strategic guidance — all from a single opening system name.
---

# Learn Chess Alex — Interactive Chess Opening Course Builder

## What This Skill Does

Given a chess opening system (e.g., "London System", "Caro-Kann", "Sicilian Najdorf"), this skill builds a complete interactive study course consisting of:

1. **Interactive Board Explorer** — Main HTML page with animated piece movement, arrow annotations showing intent (attack/defense/control/plan), and scroll-through move replay
2. **Stockfish Branch Analysis** — For every position, the engine's top 5 candidate moves with 6-ply continuations, win rate evaluation, and deviation analysis
3. **White/Black Perspective Panels** — On white's turn: subtle mistake warnings (not obvious blunders, but the tricky inaccuracies that actually lose games). On black's turn: the opponent's best options + your optimal counter
4. **Shape Page** — A separate visual guide showing the ideal piece placement, development order, strategic objective, and a checklist for when the position is "ready"

## Course Construction Pipeline

The course is built in 8 phases. Each phase depends on the previous one. Follow them in order.

### Phase 0: Research & Curate Learning Materials

Before writing a single move, search the web for high-quality teaching resources about this opening. This research has two purposes: (1) inform your own understanding so the course is accurate, (2) embed the best external resources into the course as coaching references.

**What to search for:**
- Top YouTube tutorials for this opening (e.g., GothamChess, Eric Rosen, Naroditsky, Hikaru). Search: `"{opening name}" tutorial chess youtube`. Capture: video title, channel, URL, what key concept it covers.
- Written guides with strategic explanations (lichess studies, chess.com articles, ChessCheatSheets). Search: `"{opening name}" guide strategy variations`.
- Lichess opening explorer data: `lichess.org/opening/{opening_name}` for win rates and popular continuations at different rating levels.
- Notable games by GMs who specialize in this opening (e.g., Carlsen with the London, Kasparov with the Najdorf).

**What to extract from each source:**
- Key strategic ideas the author emphasizes (these become arrow annotations and comments in the course)
- Common mistakes or traps the author warns about (these become subtle-mistake analysis targets)
- Move order nuances or "when to deviate" advice (these become dedicated variations in the explorer)
- Memorable phrases or mnemonics (these go into the Shape page)

**How to embed in the course:**
- Add a "📚 Learning Resources" section to the Shape page with links to the best 3-5 videos/articles
- Incorporate coaching insights from the videos as commentary in the interactive explorer (attribute the source, e.g., "Gotham Chess recommends...")
- If a video covers a specific variation or trap, reference it in that variation's info panel
- Use win-rate data from lichess to populate the statistical panels

This research phase ensures the course doesn't just contain raw engine analysis, but also human-friendly teaching insights from experienced coaches.

### Phase 1: Opening Research & Variation Design

Start by understanding the opening system the user wants to study. Gather:

- The main move order and key branching points
- Which side the user plays (white or black — this determines the analysis perspective)
- 4-6 major variations classified by **the opponent's intent** (not by move name)

The opponent-intent classification is the heart of this skill's teaching approach. For each variation, answer: "What is the opponent trying to achieve with this move, and what weakness does it expose in my position?"

Example classification for London System:
- "🛡️ Opponent stabilizes center" (1...d5, ...e6)
- "⚔️ Opponent challenges d4" (1...d5, ...c5)  
- "🏰 Opponent builds a wall" (1...Nf6, ...g6, ...Bg7)
- "🪞 Opponent mirrors your setup" (1...d5, ...Bf5)
- "🎭 Opponent disrupts development" (1...d5, ...Bg4)

### Phase 2: Move Verification with python-chess

Every single move sequence must be verified before building the HTML. This is non-negotiable — incorrect positions destroy the user's trust.

```python
import chess

board = chess.Board()
for uci in ["d2d4", "d7d5", "c1f4", ...]:
    move = chess.Move.from_uci(uci)
    assert move in board.legal_moves, f"ILLEGAL: {uci}"
    board.push(move)
    # Save board.board_fen() for use in HTML
```

Run verification for ALL variations before proceeding. Fix any illegal moves immediately.

### Phase 3: Stockfish Deep Analysis

Requires Stockfish binary. Ask the user for the path if not already known. The analysis produces 3 data layers:

**Layer A — Position Evaluation (all positions):**
For every position in every variation, get top 3 moves with cp scores + UCI coordinates (needed for arrow rendering).

```python
engine.analyse(board, chess.engine.Limit(depth=18), multipv=3)
```

**Layer B — Branch Exploration (all positions):**
For every position, get top 5 candidate moves. For each, simulate 6 plies of best play forward. Record the FEN at each step (needed for the branch board).

**Layer C — Subtle Mistake Detection (white/black-to-move positions only, from the user's perspective):**
Scan all legal moves. Classify by loss from best:
- 15-50cp loss → "subtle inaccuracy" 🟡 (looks reasonable but costs)
- 50-100cp loss → "calculation trap" 🟠 (needs lookahead to see the problem)  
- 100-150cp loss → "serious hidden danger" 🔴 (leads to material loss in 6-8 moves)
- Skip >150cp loss — these are obvious blunders the user won't play

For each subtle mistake, simulate 8 plies of punishment to show WHERE it goes wrong. Track the worst-drop index.

**Layer D — Opponent Response Analysis (opponent-to-move positions):**
Get top 5 opponent moves. For each, compute the user's best counter-line (6 plies). This lets the user see "if they play X, I should respond with Y→Z→W."

### Phase 4: HTML Generation

The interactive page is a single self-contained HTML file with all data embedded as JS objects. Key architecture:

**Layout:** Two-column. Left = main board + controls + SF eval panel. Right = branch explorer (unified panel that adapts based on whose turn it is).

**Main Board Features:**
- FEN-based rendering with Unicode chess pieces (♚♛♜♝♞♟), white pieces colored #fff, black #1a1a1a
- Piece slide animation on forward steps (CSS transition, 300ms ease-out)
- SVG arrow overlay for intent annotations:
  - Green = control/target squares
  - Red = attack/threat
  - Orange = weakness/risk  
  - Blue = strategic plan
  - Purple = Stockfish best move
- Yellow highlight on from/to squares of last move
- Scroll wheel on the board area advances/retreats steps
- Keyboard arrow keys also work

**Branch Explorer (right panel) — adapts by turn:**
- **User's turn:** Tabs show SF top moves (green 🐟) + subtle mistakes (🟡🟠🔴). Each tab loads its continuation into the branch board + timeline. Scroll wheel on right panel advances through that branch's steps.
- **Opponent's turn:** Tabs show opponent's top 5 options (♚). Each shows the user's best counter-line. Same scroll behavior.
- Timeline shows each step with eval bar, highlights the worst-drop step.

**SF Eval Panel (below main board):**
- Eval bar (white portion = white advantage)
- Numeric cp display
- Deviation comment: does the opening's theoretical move match SF's best? If not, explain SF's reasoning.

**Data Embedding:** All Stockfish data is embedded directly as JS const objects. No external fetches. This makes the file self-contained and works offline.

### Phase 5: Shape Page

A separate HTML file linked from the main page header. Contains:

- **Dual board comparison:** Ideal formation vs. common mistakes, with colored highlights
- **Piece development cards:** Where each piece goes and why, in priority order
- **Strategic timeline:** Phase-by-phase roadmap from opening to middlegame objective
- **Readiness checklist:** Conditions that must be true before executing the main plan
- **Mnemonic:** A memorable phrase summarizing the development order
- **📚 Learning Resources panel:** Curated links to the best video tutorials, articles, and lichess studies found in Phase 0. Each link includes a one-line summary of what it covers and which variation/concept it relates to. Group by type (Video / Article / Interactive).
- **🎓 Coaching Ideas section:** Key insights extracted from top coaches' teachings, presented as actionable tips (e.g., "Gotham Chess emphasizes: never play dxc5 in the London — it destroys your center advantage"). These are the human wisdom layer on top of the engine analysis.

### Phase 6: Move Order Principles

If relevant to the opening, create a dedicated variation in the explorer that teaches critical move-order dependencies. This is where coaching insights from Phase 0 are most valuable — coaches often emphasize move-order nuances that engines don't flag as errors.

### Phase 7: "When to Use / When to Deviate" Decision Guide

Create a variation in the explorer that helps the user decide when this opening system is the best choice and when to switch to an alternative. This is based on the opponent's first 1-2 moves. For each scenario, show on the board what happens if you continue vs. deviate. Use coaching insights from Phase 0 (e.g., "Gotham Chess recommends switching to Barry Attack against ...g6").

This phase teaches strategic flexibility — the mark of an intermediate player versus a beginner who plays the same opening regardless of context. Show both the correct order AND wrong-order demonstrations with the board, so the user can see what goes wrong.

Common patterns to check:
- Must piece X come out before pawn Y? (e.g., Bf4 before e3)
- Does early pawn push block a piece? (e.g., c3 before Nc3)
- Does knight placement affect pawn options? (e.g., Nf3 blocks f3)

## File Structure

```
output-folder/
├── {opening}-interactive.html    # Main explorer page
├── {opening}-shape.html          # Shape/formation guide
└── stockfish                     # Engine binary (user provides)
```

## Key Technical Details

### FEN Handling
Board positions use FEN board notation (the first field only, 8 ranks separated by `/`). Full FEN with turn/castling/en-passant is used internally for python-chess but only the board part is embedded in HTML.

### Arrow Coordinate System
Squares map to pixel positions: `x = file_index * SQUARE_SIZE + SQUARE_SIZE/2`, `y = (7 - rank_index) * SQUARE_SIZE + SQUARE_SIZE/2`. Arrows are SVG lines with marker-end arrowheads, shortened by ~10px from center to avoid overlapping pieces.

### Scroll Behavior
The right-panel scroll is scoped to the currently selected branch. At the first step, scrolling up does nothing (no wrap-around, no jumping to other branches). At the last step, scrolling down does nothing. This is critical for usability.

### Branch Tab Integration
White-turn and black-turn panels share the same tab bar and branch board. The `updBranches()` function checks whose turn it is and renders the appropriate content. Subtle mistakes from Layer C are merged into the tab bar alongside SF's top moves, with distinct styling (🟡🟠🔴 icons + "worst" CSS class).

## Stockfish Requirements

- Binary must be accessible at a known path
- Minimum depth 16 recommended for position eval, depth 10 acceptable for branch simulation
- python-chess library required (`pip install python-chess`)
- Analysis takes 5-15 minutes depending on number of variations and positions

## Adaptation for Different Openings

This framework works for any opening. The user specifies:
1. Opening name and main line moves
2. Which color they play
3. Key variations (or let Claude research and propose them)

The entire pipeline — verification → Stockfish analysis → HTML generation → Shape page — is the same regardless of opening. The variation classification and intent annotations are the creative part that requires chess understanding.

## References

- `references/html-template-guide.md` — Detailed HTML structure and CSS class reference
- `scripts/analyze_opening.py` — Stockfish analysis pipeline (all 4 layers)
- `scripts/generate_html.py` — HTML generation from analysis data
- `scripts/verify_moves.py` — Move legality verification
