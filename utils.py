import pickle
import re
import os
import subprocess
from collections import defaultdict
from move import Move

directory_path = os.path.abspath(os.path.dirname(__file__))

evaluation_dict = {
    "$1": "!",
    "$2": "?",
    "$3": "!!",
    "$4": "??",
    "$5": "!?",
    "$6": "?!",
    "$8": "only move",
    "$22": "Zugzwang",
    "$16": "W advantage",
    "$18": "+-",
    "$11": "=",
    "$13": "not clear",
    "$15": "little B advantage",
    "$17": "B advantage",
    "$19": "-+",
    "$44": "compensation",
    "$40": "attack",
    "$36": "initiative",
    "$132": "counterplay",
    "$138": "zeitnot",
    "$32": "development advantage",
    "$146": "N",
    "$140": "with the idea",
    "$14": "little W advantage",
}


def find_parens(s):
    toret = {}
    pstack = []

    for i, c in enumerate(s):
        if c == "(":
            pstack.append(i)
        elif c == ")":
            if len(pstack) == 0:
                raise IndexError("No matching closing parens at: " + str(i))
            toret[pstack.pop()] = i

    if len(pstack) > 0:
        raise IndexError("No matching opening parens at: " + str(pstack.pop()))

    return toret


def construct_tree(move, pgn, nb, file_header):
    if len(nb) == 0:
        return
    if pgn[nb[0].start() - 1] == "(":
        start_bracket_idx = pgn.find("{", pgn.find(" ", nb[0].end() + 1))
        end_bracket_idx = pgn.find("}", start_bracket_idx)
        comment = pgn[start_bracket_idx + 2 : end_bracket_idx - 1]
        fen = None
        evaluation_idx = pgn.find(
            "$", pgn.find(" ", nb[0].end() + 1), start_bracket_idx
        )
        if pgn.find("{", end_bracket_idx, end_bracket_idx + 3) > -1:
            fen = pgn[
                pgn.find("{", end_bracket_idx) + 2 : pgn.find("}", end_bracket_idx + 1)
            ]

        new_move = Move(
            pgn[nb[0].start() : pgn.find(" ", nb[0].end() + 1)],
            parent=move.parent,
            fen=fen if fen is not None else comment,
            comments=comment if fen is not None else None,
            evaluation=(
                pgn[evaluation_idx:start_bracket_idx].split(" ")[:-1]
                if evaluation_idx >= 0
                else None
            ),
            main_variant=False,
        )
        Move.add_child(move.parent, new_move)
        ending_parenthesis = find_parens(pgn)[nb[0].start() - 1]
        sub_pgn = pgn[nb[0].start() : ending_parenthesis]
        new_nb = list(re.finditer(r"\d+\.+(?![^{]*})", sub_pgn))
        new_nb.pop(0)
        construct_tree(new_move, sub_pgn, new_nb, None)
        return construct_tree(
            move,
            pgn[ending_parenthesis + 1 :],
            list(re.finditer(r"\d+\.+(?![^{]*})", pgn[ending_parenthesis + 1 :])),
            None,
        )
    else:
        start_bracket_idx = pgn.find("{", pgn.find(" ", nb[0].end() + 1))
        end_bracket_idx = pgn.find("}", start_bracket_idx)
        comment = pgn[start_bracket_idx + 2 : end_bracket_idx - 1]
        fen = None
        evaluation_idx = pgn.find(
            "$", pgn.find(" ", nb[0].end() + 1), start_bracket_idx
        )
        if pgn.find("{", end_bracket_idx, end_bracket_idx + 3) > -1:
            fen = pgn[
                pgn.find("{", end_bracket_idx) + 2 : pgn.find("}", end_bracket_idx + 1)
            ]

        new_move = Move(
            pgn[nb[0].start() : pgn.find(" ", nb[0].end() + 1)],
            parent=move,
            fen=fen if fen is not None else comment,
            comments=comment if fen is not None else None,
            evaluation=(
                pgn[evaluation_idx:start_bracket_idx].split(" ")[:-1]
                if evaluation_idx >= 0
                else None
            ),
            main_variant=True,
            file_header=file_header if pgn[0:3] == "1. " else None
        )
        Move.add_child(move, new_move)
        nb.pop(0)
        construct_tree(new_move, pgn, nb, None)


def read_and_build_tree():
    while True:
        fake_move = Move("", fen="w ")
        try:
            for file in os.listdir(directory_path + r"\pgns"):
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

                    temp_pgn = open(full_path_file + "_temp.pgn", encoding="utf-8")
                    fen_pgn = temp_pgn.read()
                    temp_pgn.close()
                    header_file = open(full_path_file, encoding="utf-8")
                    header_pgn = header_file.read()
                    header_file.close()
                    file_header = header_pgn[0:header_pgn.find("\n\n")]
                    fen_pgn = fen_pgn.replace("\n", " ")
                    fen_pgn = re.sub(
                        r"\( \d+\.",
                        lambda match: match.group(0).replace(" ", ""),
                        fen_pgn,
                    )

                    fen_pgn = fen_pgn[fen_pgn.find("1. ") :]
                    # print(fen_pgn)

                    # find all the main moves number and put it in the nb list
                    nb = list(re.finditer(r"\d+\.+(?![^{]*})", fen_pgn))
                    construct_tree(fake_move, fen_pgn, nb, file_header)
            remove_temp_pgn()
            return fake_move
        except subprocess.CalledProcessError as inst:
            print(
                "--------------------- ERROR: " + str(inst) + " ---------------------"
            )
            remove_temp_pgn()


def repertoire_to_pgn(b_or_w):
    with open(
            os.path.join(
                directory_path + r"\repertoire\\", b_or_w + ".repertoire.pickle"
            ),
            "rb",
        ) as handle:
        fake_move: Move = pickle.load(handle)
    for i, child in enumerate(fake_move.children):
        if child.file_header:
            white_idx = child.file_header.find("White ")
            black_idx = child.file_header.find("Black ")
            if child.file_header[white_idx+7] != "?":
                file_name = child.file_header[white_idx+7:child.file_header.find("\"", white_idx+7)]
            elif child.file_header[black_idx+7] != "?":
                file_name = child.file_header[black_idx+7:child.file_header.find("\"", black_idx+7)]
            else:
                raise ValueError("There is a problem with the file header:\n"+child.file_header)
            file_name = "("+str(i+1)+")"+file_name+".pgn"
            print(file_name)
            write_pgn = open(directory_path + r"\pgns\\" + file_name, "w", encoding="utf-8")
            write_pgn.write(child.file_header+"\n\n")
            write_pgn.write(build_pgn_move(child)+" *\n\n")
            write_pgn.close()

def build_pgn_move(move: Move | None, only_children = False) -> str:
    if move is None:
        return ""
    if only_children:
        move_str=""
    else:
        move_str = build_move_unitary(move)
    if move.children:
        move.children.sort(key=lambda c: int(not c.main_variant))
        move_str+=" "+build_move_unitary(move.children[0])
        for c in move.children[1:]:
            move_str+=" ("
            move_str+=build_pgn_move(c)
            move_str+=")"
        move_str+= build_pgn_move(move.children[0], True)
    else:
        return move_str
    return move_str


def build_move_unitary(move: Move):
    comment = ""
    if move.comments is not None:
        comment = " {"+move.comments+"}"
    move_eval = ""
    if move.evaluation is not None:
        move_eval = " "+" ".join(move.evaluation)
    return move.name + comment + move_eval


def traversal_tree(move, fens, moves):
    if move is not None:
        # get the fen with the color but without the move order, castle, etc. to find transposition
        fens.append(move.fen[: move.fen.find(" ", move.fen.find(" ") + 1)])
        moves.append(move)
        for child in move.children:
            traversal_tree(child, fens, moves)
    return fens, moves


def french_chess(string):
    last = (
        string.replace("N", "C")
        .replace("B", "F")
        .replace("R", "T")
        .replace("Q", "D")
        .replace("K", "R")
    )
    last = re.sub(r"\.\ ", ".", last)
    last = re.sub(r"\d+\.\.\.", "", last)
    return last


def is_not_a_bad_move(move):
    if move.evaluation is None:
        return True
    if len(list(set(move.evaluation).intersection(["$4", "$2", "$6"]))) > 0:
        return False
    return True


def remove_temp_pgn(path=directory_path + r"\pgns"):
    for file in os.listdir(path):
        if file.endswith("_temp.pgn"):
            if os.path.exists(path + "\\" + file):
                os.remove(path + "\\" + file)


def find_all_children(
    transposition_dict, fen, moves, move_idx, remove_from_dict=False
) -> list[Move]:
    all_children = moves[move_idx].children
    if fen in list(transposition_dict.keys()):
        # the fen is found in other files
        all_children = []
        for idx in transposition_dict[fen]:
            all_children += moves[idx].children
        if remove_from_dict:
            transposition_dict.pop(fen)
    return list(set(all_children))


def build_fen_dict(fens):
    D = defaultdict(list)
    for i, item in enumerate(fens):
        D[item].append(i)
    return {k: v for k, v in D.items() if len(v) > 1}


def pgn_to_evaluation(evaluation):
    beautiful_str = ""
    if evaluation is None:
        return ""
    for idx, chess_eval in enumerate(evaluation):
        if idx != 0:
            beautiful_str += " "
        if chess_eval in list(evaluation_dict.keys()):
            beautiful_str += evaluation_dict[chess_eval]
        else:
            beautiful_str += chess_eval
    return beautiful_str


def move_full_print(move):
    return (
        move.name.replace("N", "C")
        .replace("B", "F")
        .replace("R", "T")
        .replace("Q", "D")
        .replace("K", "R")
        + (" " + pgn_to_evaluation(move.evaluation) if move.evaluation else "")
        + (" " + move.comments if move.comments else "")
    )
