# HTML Template Structure Reference

## Main Explorer Page Architecture

The interactive page is a single self-contained HTML file. All data (variations, Stockfish analysis) is embedded as JavaScript `const` objects.

### Data Objects

```javascript
const BM = {...};  // Black move analysis (Layer D)
const WM = {...};  // White subtle mistakes (Layer C)
const SF = {...};  // Branch exploration (Layers A+B)
const V  = {...};  // Variation definitions with moves, FENs, comments, arrows
```

### Variation Definition Format

```javascript
'variation_key': {
  n: '🛡️ Display Name',     // emoji + name for tab button
  cat: 'Category Label',     // shown as subtitle
  sk: 'sf_data_key',         // key into SF/WM/BM data objects
  info: {
    intent: 'What the opponent is trying to do',
    weakness: ['Your exposed weaknesses'],
    target: ['Your attack targets'],
    response: ['Your best responses'],
    winrate: [white%, draw%, black%]
  },
  mv: [
    {
      m: 'Move label',        // e.g., "1.d4", "1...d5"
      fen: 'FEN board string', // 8 ranks separated by /
      f: 'from_square',       // e.g., "d2" (empty string for starting position)
      t: 'to_square',         // e.g., "d4"
      c: 'Commentary text',   // shown below the board
      a: [                    // arrows to draw on this step
        {from: 'd4', to: 'e5', color: 'green'}
      ],
      d: [                    // dots to highlight on squares
        {sq: 'e5', color: 'green'}
      ]
    }
  ]
}
```

### Arrow Colors

| Color    | CSS Hex   | Meaning              | SVG Marker ID |
|----------|-----------|----------------------|---------------|
| green    | #4caf50   | Control / target     | ag            |
| red      | #ef5350   | Attack / threat      | ar            |
| orange   | #ffa726   | Weakness / risk      | ao            |
| blue     | #42a5f5   | Plan / strategy      | ab            |
| purple   | #ce93d8   | Stockfish best move  | ap            |

### Board Rendering

- Square size: 40px (configurable via `SZ` constant)
- Light squares: `#e8d5a8`, Dark squares: `#b58863`
- Last-move highlight: from=`#aaa34e`, to=`#cdd26a`
- White pieces: `color: #fff` with dark text-shadow
- Black pieces: `color: #1a1a1a` with no shadow
- All pieces use filled Unicode symbols (♚♛♜♝♞♟), differentiated by color class

### Piece Animation

On forward step (scroll down / right arrow):
1. Render the new FEN but skip the piece at the destination square
2. Create an absolutely positioned element at the origin square
3. Set CSS transition (300ms ease-out) and update left/top to destination
4. After 300ms, remove the floating element and render the full board

### Scroll Behavior Rules

- Left board area: scroll = advance/retreat main line steps
- Right panel area: scroll = advance/retreat within selected branch ONLY
- At first step of a branch, scroll up = do nothing (no wrap, no jump)
- At last step of a branch, scroll down = do nothing
- Switching tabs or main steps resets branch scroll to step 0

### Branch Explorer Logic

The `updBranches(vk, idx)` function checks whose turn it is:

**User's turn:**
- Tabs = SF top moves (green `rank1` class) + subtle mistakes (🟡🟠🔴 `worst` class)
- Clicking SF tab → `renderBranch()` shows PV line
- Clicking subtle tab → `renderSubtleBranch(idx)` shows consequence line with ⚠️ drop markers

**Opponent's turn:**
- Tabs = opponent's top 5 options (♚ prefix)
- Clicking tab → `renderBlackBranch(opt)` shows user's counter-line
- Timeline alternates ♔/♚ icons to show who moves

### CSS Class Quick Reference

| Class    | Element      | Purpose                        |
|----------|-------------|--------------------------------|
| .brd     | Board grid  | 8x8 grid container             |
| .s       | Square      | Individual square               |
| .l / .d  | Square      | Light / dark square color       |
| .wp / .bp| Square      | White / black piece color       |
| .lf / .lt| Square      | Last-from / last-to highlight   |
| .nb / .a | Nav button  | Navigation tab / active state   |
| .bt      | Branch tab  | Branch selector                 |
| .rank1   | Branch tab  | Best move (green left border)   |
| .worst   | Branch tab  | Worst option (red left border)  |
| .bstep   | Timeline    | One step in branch timeline     |
| .drop    | Timeline    | Marks the worst-drop step       |

## Shape Page Architecture

Separate HTML file. Contains:
- Dual board comparison (good vs bad formation)
- Piece development cards with priority order
- Timeline showing phases from opening to middlegame
- Readiness checklist
- Mnemonic summary

Board highlights use CSS classes: `glow-green` (correct), `glow-gold` (key square), `glow-blue` (target), `glow-red` (mistake).
