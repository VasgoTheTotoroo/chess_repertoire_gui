"""Subprocess of stockfish"""

import os
import sys
import re
import asyncio
import chess
import chess.engine

directory_path = os.path.abspath(os.path.dirname(__file__))


async def main(fen):
    mulitpv = 4
    max_depth = 30
    threads = 12
    hash = 33554
    moves_score_str = {}

    board = chess.Board(fen)
    _, engine = await chess.engine.popen_uci(
        r"c:\Users\Vassia\Desktop\echec\stockfish\stockfish-windows-x86-64.exe"
    )
    await engine.configure({"Threads": threads})
    await engine.configure({"Hash": hash})
    with await engine.analysis(board=board, multipv=mulitpv) as analysis:
        async for info in analysis:
            current_depth = info.get("depth", 0)
            if info.get("depth", 0) > max_depth:
                break
            if info.get("score") is not None:
                pv_str = ""
                variation = board.variation_san(info.get("pv")[:30])  # type: ignore
                variation = re.sub(r"\.\ ", ".", variation)
                pv_str += (
                    str(info.get("score").white().score(mate_score=300) / 100) + " / "  # type: ignore
                )
                pv_str += variation
                moves_score_str[info.get("multipv")] = pv_str
                sf_log = open(directory_path + r"\stockfish.txt", "w", encoding="utf-8")
                sf_log.write(
                    "profondeur : "
                    + str(current_depth)
                    + "\n"
                    + str(moves_score_str).replace(", ", "\n").replace("'", "")[1:-1]
                )
                sf_log.close()
    await engine.quit()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
