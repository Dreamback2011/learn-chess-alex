#!/usr/bin/env python3
"""
Stockfish analysis pipeline for chess opening study.
Produces 4 analysis layers:
  A) Position evaluation (top 3 + coordinates)
  B) Branch exploration (top 5 x 6-ply continuations)
  C) Subtle mistake detection (user's perspective, 15-150cp loss range)
  D) Opponent response analysis (opponent's top 5 + user's counter-line)
"""
import chess
import chess.engine
import json
import sys
import argparse

def analyze_layer_ab(engine, board, depth=18, multipv_top=5, branch_depth=6):
    """Layers A+B: position eval + branch exploration."""
    info = engine.analyse(board, chess.engine.Limit(depth=depth),
                          multipv=min(multipv_top, len(list(board.legal_moves))))
    if not isinstance(info, list):
        info = [info]

    branches = []
    for mi in info[:multipv_top]:
        pv = mi.get("pv", [])
        s = mi["score"].white()
        cp = s.score(mate_score=10000) if s else 0
        if not pv:
            continue

        first = pv[0]
        san = board.san(first)

        # Simulate branch forward
        sim = board.copy()
        line = []
        worst_drop = 0
        worst_idx = 0
        for pi, mv in enumerate(pv[:branch_depth]):
            mv_san = sim.san(mv)
            sim.push(mv)
            ev = engine.analyse(sim, chess.engine.Limit(depth=10))
            ecp = ev["score"].white().score(mate_score=10000)
            drop = abs(ecp - cp)
            if drop > worst_drop:
                worst_drop = drop
                worst_idx = pi
            line.append({"s": mv_san, "f": sim.board_fen(), "c": ecp})

        branches.append({
            "s": san,
            "fr": chess.square_name(first.from_square),
            "to": chess.square_name(first.to_square),
            "c": cp,
            "l": line,
            "wd": worst_drop,
            "wi": worst_idx
        })

    return {
        "c": branches[0]["c"] if branches else 0,
        "t": "w" if board.turn == chess.WHITE else "b",
        "b": branches
    }

def analyze_layer_c(engine, board, user_is_white=True, depth=16):
    """Layer C: subtle mistake detection for the user's side."""
    # Only analyze when it's the user's turn
    is_user_turn = (board.turn == chess.WHITE) == user_is_white
    if not is_user_turn:
        return None

    legal = list(board.legal_moves)
    move_evals = []
    for m in legal:
        san = board.san(m)
        board.push(m)
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        cp = info["score"].white().score(mate_score=10000)
        board.pop()
        move_evals.append({"san": san, "uci": m.uci(), "cp": cp})

    # Sort from user's perspective
    if user_is_white:
        move_evals.sort(key=lambda x: x["cp"], reverse=True)
    else:
        move_evals.sort(key=lambda x: x["cp"])  # lower = better for black

    best_cp = move_evals[0]["cp"] if move_evals else 0
    bests = [{"s": m["san"], "c": m["cp"]} for m in move_evals[:2]
             if abs(best_cp - m["cp"]) <= 10]

    # Find subtle mistakes (15-150cp loss)
    subtle = []
    for me in move_evals:
        loss = abs(best_cp - me["cp"])
        if 15 <= loss <= 150:
            sim = board.copy()
            sim.push(chess.Move.from_uci(me["uci"]))
            info_pv = engine.analyse(sim, chess.engine.Limit(depth=14))
            pv = info_pv.get("pv", [])

            line = []
            worst_cp = me["cp"]
            worst_idx = -1
            for pi, pm in enumerate(pv[:8]):
                san_pv = sim.san(pm)
                sim.push(pm)
                ev = engine.analyse(sim, chess.engine.Limit(depth=10))
                ecp = ev["score"].white().score(mate_score=10000)
                if (user_is_white and ecp < worst_cp) or (not user_is_white and ecp > worst_cp):
                    worst_cp = ecp
                    worst_idx = pi
                line.append({"s": san_pv, "f": sim.board_fen(), "c": ecp})

            total_loss = abs(best_cp - worst_cp)
            tag = "subtle" if loss <= 50 else "inaccuracy" if loss <= 100 else "serious"

            subtle.append({
                "s": me["san"], "c": me["cp"], "loss": loss, "tag": tag,
                "wc": worst_cp, "wi": worst_idx, "tl": total_loss, "l": line
            })

    return {"step": -1, "bc": best_cp, "bests": bests, "sub": subtle[:6]}

def analyze_layer_d(engine, board, user_is_white=True, depth=16):
    """Layer D: opponent response analysis."""
    is_opponent_turn = (board.turn == chess.WHITE) != user_is_white
    if not is_opponent_turn:
        return None

    info = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=5)
    if not isinstance(info, list):
        info = [info]

    opts = []
    for mi in info[:5]:
        pv = mi.get("pv", [])
        s = mi["score"].white()
        cp = s.score(mate_score=10000) if s else 0
        if not pv:
            continue

        opp_move = pv[0]
        opp_san = board.san(opp_move)

        sim = board.copy()
        sim.push(opp_move)
        resp_info = engine.analyse(sim, chess.engine.Limit(depth=14))
        resp_pv = resp_info.get("pv", [])

        response_line = []
        for rm in resp_pv[:6]:
            r_san = sim.san(rm)
            sim.push(rm)
            ev = engine.analyse(sim, chess.engine.Limit(depth=10))
            ecp = ev["score"].white().score(mate_score=10000)
            response_line.append({"s": r_san, "f": sim.board_fen(), "c": ecp})

        opts.append({"s": opp_san, "c": cp, "l": response_line})

    return {"step": -1, "opts": opts}

def analyze_full(engine, variations, user_is_white=True, depth=18):
    """Run all 4 layers for all variations."""
    results = {"branches": {}, "subtle": {}, "opponent": {}}

    for var_name, uci_moves in variations.items():
        print(f"\n=== {var_name} ===")
        board = chess.Board()
        br_data, sub_data, opp_data = [], [], []

        for step_idx in range(len(uci_moves) + 1):
            # Layer A+B
            ab = analyze_layer_ab(engine, board, depth=depth)
            br_data.append(ab)

            # Layer C
            c = analyze_layer_c(engine, board, user_is_white, depth=min(depth, 16))
            if c:
                c["step"] = step_idx
                sub_data.append(c)

            # Layer D
            d = analyze_layer_d(engine, board, user_is_white, depth=min(depth, 16))
            if d:
                d["step"] = step_idx
                opp_data.append(d)

            print(f"  Step {step_idx}: cp={ab['c']}, turn={ab['t']}")

            if step_idx < len(uci_moves):
                board.push(chess.Move.from_uci(uci_moves[step_idx]))

        results["branches"][var_name] = br_data
        results["subtle"][var_name] = sub_data
        results["opponent"][var_name] = opp_data

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stockfish opening analysis")
    parser.add_argument("variations", help="JSON file with variations {name: [uci_moves]}")
    parser.add_argument("stockfish", help="Path to Stockfish binary")
    parser.add_argument("-o", "--output", default="analysis.json", help="Output JSON file")
    parser.add_argument("-d", "--depth", type=int, default=18, help="Analysis depth")
    parser.add_argument("--black", action="store_true", help="User plays black (default: white)")
    args = parser.parse_args()

    with open(args.variations) as f:
        variations = json.load(f)

    engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    engine.configure({"Threads": 2, "Hash": 128})

    results = analyze_full(engine, variations, user_is_white=not args.black, depth=args.depth)

    engine.quit()

    with open(args.output, "w") as f:
        json.dump(results, f)

    print(f"\nAnalysis saved to {args.output}")
