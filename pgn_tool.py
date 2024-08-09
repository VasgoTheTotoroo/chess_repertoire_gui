"""This module is the main module of the project.
It implements the main loop of the game and the CLI usage"""

import os
import re
import subprocess
import sys
import textwrap
import csv
import locale
from move import Move
from window import Window
from utils import (
    build_fen_dict,
    find_all_children,
    french_chess,
    is_not_a_bad_move,
    read_and_build_tree,
    remove_temp_pgn,
    repertoire_to_pgn,
    save_to_repertoire,
    traversal_tree,
)


def main(usecase):
    """Main method of the program, start the game and implements the CLI usages"""

    directory_path = os.path.abspath(os.path.dirname(__file__))
    is_french = locale.getlocale()[0] == "fr_FR"

    # find all the transpositions in the pgn files
    if usecase == "find_transpositions":
        fake_move = read_and_build_tree()

        fens = []
        moves = []
        traversal_tree(fake_move, fens, moves)

        transposition_dict = build_fen_dict(fens)
        transposition_dict = list(transposition_dict.values())

        true_duplicates = []
        for d in transposition_dict:
            nb_comments = 0
            for idx in d:
                if moves[idx].comments is not None:
                    if moves[idx].comments.find("Transposition") > -1:
                        nb_comments += 1
                if moves[idx].parent.comments is not None:
                    if moves[idx].parent.comments.find("Transposition") > -1:
                        nb_comments += 1
                if len(moves[idx].children) > 0:
                    for move in moves[idx].children:
                        if move.comments:
                            if move.comments.find("Transposition") > -1:
                                nb_comments += 1
            if nb_comments < len(d) - 1:
                true_duplicates.append(d)

        print(true_duplicates)

        for i, duplication in enumerate(reversed(true_duplicates)):
            strings = []
            for idx in duplication:
                if is_french:
                    strings.append(
                        "Transposition " + french_chess(moves[idx].str_to_root())
                    )
                else:
                    strings.append("Transposition " + moves[idx].str_to_root())
            # Remove mates and draw repetition moves
            if strings[1].find(strings[0]) > -1 or strings[0][-1] == "#":
                # print("REPETITION OR MATE")
                # for s in strings:
                #     print(s)
                pass
            elif len(strings) > 2 and strings[2].find(strings[0]) > -1:
                pass
            else:
                print("duplication " + str(i) + ":\n")
                for s in strings:
                    print(s)
                print("\n")

    # find all the deviationin the pgn files
    elif usecase == "find_deviations":
        if len(sys.argv) < 3:
            raise ValueError("You need to provide a color argument for find_deviations")
        fake_move = read_and_build_tree()
        fens = []
        moves = []
        traversal_tree(fake_move, fens, moves)

        transposition_dict = build_fen_dict(fens)

        color = sys.argv[2]
        if color != "w" and color != "b":
            raise ValueError("The color argument is not b or w")
        deviation = 1
        for idx, fen in enumerate(fens):
            all_children = find_all_children(transposition_dict, fen, moves, idx, True)
            if (
                len(fen) > 0
                and len(list(filter(is_not_a_bad_move, all_children))) > 1
                and fen[-1] == color
            ):
                print("-----deviation " + str(deviation) + "-----")
                deviation = deviation + 1
                for c in all_children:
                    if is_french:
                        print(
                            french_chess(c.str_to_root())
                            + (" " + c.comments if c.comments else "")
                        )
                    else:
                        print(
                            c.str_to_root() + (" " + c.comments if c.comments else "")
                        )

    # split the pgn file exported from chessbase to one pgn per game
    elif usecase == "split_pgn":
        if len(sys.argv) < 3:
            raise ValueError(
                """You need to provide a file name argument for split_pgn. 
                The file need to be in the pgn subdirectory"""
            )
        file_name = sys.argv[2]
        file = open(directory_path + r"\pgns\\" + file_name, encoding="utf-8")
        file_str = file.read().split('[Event "')

        for i, s in enumerate(file_str[1:]):
            idx_name = s.find("[White") + 8
            splitted_file = "\n".join(textwrap.wrap(s[s.find("\n\n") :], 70))
            color_name = "White"
            if s[idx_name] == "?":
                # We take for name of the file what is between the Black square brackets
                # in the pgn if there is nothing in the White
                color_name = "Black"
            file_name = (
                "("
                + str(i + 1)
                + ") "
                + s[
                    s.find("[" + color_name)
                    + 8 : s.find('"', s.find("[" + color_name) + 8)
                ]
                + ".pgn"
            )
            print(file_name)
            f = open(
                os.path.join(directory_path + r"\pgns\\", file_name),
                "w",
                encoding="utf-8",
            )
            f.write(s[: s.find("\n\n") + 2] + splitted_file)
            f.close()
        file.close()

    # save your pgns to a repertoire file
    elif usecase == "save_to_repertoire":
        if len(sys.argv) < 3:
            raise ValueError(
                """You need to provide a color argument for save_to_repertoire. 
                The file will be then saved under \repertoire\\[w/b].repertoire.pickle"""
            )
        b_or_w = sys.argv[2]
        if b_or_w != "w" and b_or_w != "b":
            raise ValueError("The color argument is not b or w")
        fake_move = read_and_build_tree()
        save_to_repertoire(b_or_w, fake_move)

    # Fill opening names into your pgns
    elif usecase == "fill_opening_names":
        eco_codes = []
        for file in os.listdir(directory_path + r"\chess-openings"):
            if file.endswith(".tsv"):
                full_path_file = directory_path + r"\chess-openings\\" + file
                tab_file = open(full_path_file, encoding="utf-8")
                tsv_file = csv.reader(tab_file, delimiter="\t")
                for line in tsv_file:
                    if line[0] != "eco":
                        truncated_fen = line[4][0 : line[4].find(" ") + 2]
                        eco_codes.append([line[1], truncated_fen])
                tab_file.close()

        for file in os.listdir(directory_path + r"\pgns"):
            fake_move = Move("", fen="w ")
            full_path_file = directory_path + r"\pgns\\" + file
            if file.endswith(".pgn") and file != "game1.pgn":
                subprocess.check_call(
                    [
                        directory_path + r"\pgn-extract.exe",
                        "-F",
                        "--fencomments",
                        full_path_file,
                        "-o",
                        full_path_file + "_temp.pgn",
                    ]
                )

                temp_pgn = open(full_path_file + "_temp.pgn", "r", encoding="utf-8")
                fen_pgn = temp_pgn.read().replace("\n", " ")
                temp_pgn.close()
                fen_pgn = re.sub(
                    r"\( \d+\.", lambda match: match.group(0).replace(" ", ""), fen_pgn
                )
                for opening in eco_codes:
                    fen_idx = fen_pgn.find(opening[1])
                    if fen_idx != -1:
                        # if there is no comment already on the move
                        if fen_pgn[fen_idx - 4] != "}":
                            fen_pgn = (
                                fen_pgn[: fen_idx - 3]
                                + " { "
                                + opening[0]
                                + " }"
                                + fen_pgn[fen_idx - 3 :]
                            )
                        else:
                            fen_pgn = (
                                fen_pgn[: fen_idx - 4]
                                + opening[0]
                                + " "
                                + fen_pgn[fen_idx - 4 :]
                            )
                fen_pgn = re.sub(r"(?<=\{)[^}]*\/+[^}]*(?=\})", "", fen_pgn)
                fen_pgn = fen_pgn.replace("{}", "").replace("]", "]\n")
                write_pgn = open(full_path_file, "w", encoding="utf-8")
                write_pgn.write(fen_pgn)
                write_pgn.close()
        remove_temp_pgn()
    elif usecase == "export_repertoire":
        if len(sys.argv) < 3:
            raise ValueError(
                """You need to provide a color argument for export_repertoire. 
                The file will be then saved under \\pgns"""
            )
        b_or_w = sys.argv[2]
        if b_or_w != "w" and b_or_w != "b":
            raise ValueError("The color argument is not b or w")
        repertoire_to_pgn(b_or_w)
        print("repertoire exported to pgns!")
    else:
        raise ValueError("The argument you passed to the program is not known")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Play a game (GUI)
        Window()
    else:
        main(sys.argv[1])
