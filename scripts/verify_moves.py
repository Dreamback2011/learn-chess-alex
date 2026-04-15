#!/usr/bin/env python3
"""Verify all move sequences are legal and output FENs for each position."""
import chess
import json
import sys

def verify_variation(name, uci_moves):
    """Verify a sequence of UCI moves and return FENs."""
    board = chess.Board()
    results = [{"step": 0, "fen": board.board_fen(), "full_fen": board.fen()}]

    for i, uci in enumerate(uci_moves):
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            similar = [m.uci() for m in board.legal_moves if m.uci()[:2] == uci[:2]]
            return {"ok": False, "error": f"Step {i+1} ({uci}) is ILLEGAL in {name}",
                    "similar": similar, "fen": board.board_fen()}
        san = board.san(move)
        board.push(move)
        results.append({
            "step": i + 1,
            "uci": uci,
            "san": san,
            "fen": board.board_fen(),
            "full_fen": board.fen(),
            "turn": "w" if board.turn == chess.WHITE else "b"
        })

    return {"ok": True, "name": name, "positions": results}

def verify_all(variations_dict):
    """Verify all variations. variations_dict = {name: [uci_moves]}"""
    all_ok = True
    all_results = {}

    for name, moves in variations_dict.items():
        result = verify_variation(name, moves)
        if result["ok"]:
            print(f"  ✓ {name}: {len(moves)} moves OK")
            all_results[name] = result["positions"]
        else:
            print(f"  ✗ {result['error']}")
            if result.get("similar"):
                print(f"    Did you mean: {result['similar']}")
            all_ok = False

    return all_ok, all_results

if __name__ == "__main__":
    # Example usage: python verify_moves.py input.json output.json
    if len(sys.argv) < 2:
        print("Usage: python verify_moves.py <variations.json> [output.json]")
        print("variations.json format: {\"name\": [\"d2d4\", \"d7d5\", ...]}")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        variations = json.load(f)

    ok, results = verify_all(variations)

    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nFENs saved to {sys.argv[2]}")

    sys.exit(0 if ok else 1)
