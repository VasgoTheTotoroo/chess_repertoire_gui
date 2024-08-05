import subprocess
import re
from collections import defaultdict
import os
import sys

# C:\Users\vassia\Desktop\echec\transposition_finder\transposition_finder.py
# C:\Users\vassia\Desktop\echec\transposition_finder\split_pgn.py "game1.txt"
# C:\Users\vassia\Desktop\echec\transposition_finder\deviation_finder.py

class Move():
    def __init__(self, name, fen=None, comments=None, parent=None, evaluation=None):
        self.name = name
        self.parent = parent
        self.fen = fen
        self.comments = comments
        self.evaluation = evaluation
        self.children = []

    def __str__(self, com_fen=False, full_str = True) -> str:
        str_add = ""
        if com_fen:
            str_add = "("+str(self.comments)+ " "+str(self.fen)+")"
        if full_str:
            if len(self.children) == 1:
                return self.name+" "+str_add+self.children[0].__str__()
            if len(self.children) > 1:
                string = self.name+" "+str_add
                for i, c in enumerate(self.children):
                    if i>0:
                        string+="\n"+c.get_depth()*7*" "+"|--"
                    string+=c.__str__()
                return string
        return self.name+" "+str_add

    def __repr__(self) -> str:
        return self.__str__()

    def add_child(self, child):
        self.children.append(child)

    def get_depth(self):
        if self.parent is None:
            return 0
        return 1+self.parent.get_depth()

    def __eq__(self, __value: object) -> bool:
        fen1 = self.fen[:self.fen.find(" ", self.fen.find(" ")+1)]
        fen2 = __value.fen[:__value.find(" ", __value.fen.find(" ")+1)]
        # print("1:"+fen1)
        # print("2:"+fen2)
        if fen1 == fen2:
            return True
        return False

    def str_to_root(self):
        if self.parent is None:
            return self.name
        string = self.name
        return self.parent.str_to_root()+" "+string

def find_parens(s):
    toret = {}
    pstack = []

    for i, c in enumerate(s):
        if c == '(':
            pstack.append(i)
        elif c == ')':
            if len(pstack) == 0:
                raise IndexError("No matching closing parens at: " + str(i))
            toret[pstack.pop()] = i

    if len(pstack) > 0:
        raise IndexError("No matching opening parens at: " + str(pstack.pop()))

    return toret

def construct_tree(move, pgn, nb):
    if len(nb) == 0:
        return
    if pgn[nb[0].start()-1] == "(":
        start_bracket_idx = pgn.find('{', pgn.find(" ",nb[0].end()+1))
        end_bracket_idx = pgn.find('}', start_bracket_idx)
        comment = pgn[start_bracket_idx+2: end_bracket_idx-1]
        fen = None
        evaluation_idx = pgn.find("$", pgn.find(" ",nb[0].end()+1), start_bracket_idx)
        if pgn.find('{', end_bracket_idx, end_bracket_idx+3) > -1:
            fen = pgn[pgn.find('{', end_bracket_idx)+2: pgn.find('}', end_bracket_idx+1)]
        new_move = Move(pgn[nb[0].start(): pgn.find(" ",nb[0].end()+1)],
                        parent=move.parent,
                        fen = fen if fen is not None else comment,
                        comments = comment if fen is not None else None,
                        evaluation = pgn[evaluation_idx: pgn.find(" ", evaluation_idx)] if evaluation_idx >= 0 else None)
        # print("m="+str(move))
        # print("nm="+str(new_move))
        Move.add_child(move.parent, new_move)
        ending_parenthesis = find_parens(pgn)[nb[0].start()-1]
        sub_pgn = pgn[nb[0].start(): ending_parenthesis]
        new_nb = list(re.finditer(r"\d+\.+(?![^{]*})", sub_pgn))
        new_nb.pop(0)
        construct_tree(new_move, sub_pgn, new_nb)
        return construct_tree(move,
                              pgn[ending_parenthesis+1:],
                              list(re.finditer(r"\d+\.+(?![^{]*})", pgn[ending_parenthesis+1:])))
    else:
        start_bracket_idx = pgn.find('{', pgn.find(" ",nb[0].end()+1))
        end_bracket_idx = pgn.find('}', start_bracket_idx)
        comment = pgn[start_bracket_idx+2: end_bracket_idx-1]
        fen = None
        evaluation_idx = pgn.find("$", pgn.find(" ",nb[0].end()+1), start_bracket_idx)
        if pgn.find('{', end_bracket_idx, end_bracket_idx+3) > -1:
            fen = pgn[pgn.find('{', end_bracket_idx)+2: pgn.find('}', end_bracket_idx+1)]

        new_move = Move(pgn[nb[0].start(): pgn.find(" ",nb[0].end()+1)],
                        parent=move,
                        fen = fen if fen is not None else comment,
                        comments = comment if fen is not None else None,
                        evaluation = pgn[evaluation_idx: pgn.find(" ", evaluation_idx)] if evaluation_idx >= 0 else None)
        Move.add_child(move, new_move)
        nb.pop(0)
        construct_tree(new_move, pgn, nb)

fake_move = Move("", fen="")

for file in os.listdir(os.getcwd()):
    if file.endswith(".pgn"):
        subprocess.check_call([r"C:\Users\vassia\Desktop\echec\transposition_finder\pgn-extract.exe", "-F", "--fencomments", file, "-o", file+"_temp.pgn"])

        temp_pgn = open(file+"_temp.pgn",  encoding="utf-8")
        fen_pgn = temp_pgn.read().replace('\n', ' ')
        temp_pgn.close()
        fen_pgn = re.sub(r"\( \d+\.", lambda match: match.group(0).replace(" ",""), fen_pgn)

        fen_pgn = fen_pgn[fen_pgn.find("1. "):]
        # print(fen_pgn)

        nb = list(re.finditer(r"\d+\.+(?![^{]*})", fen_pgn))
        construct_tree(fake_move, fen_pgn, nb)

fens = []
moves = []
def traversal_tree(move):
    if move is not None:
        fens.append(move.fen[:move.fen.find(" ", move.fen.find(" ")+1)])
        moves.append(move)
        for child in move.children:
            traversal_tree(child)
def french_chess(string):
    last = string.replace("N", "C").replace("B", "F").replace("R", "T").replace("Q", "D").replace("K", "R")
    last = re.sub(r"\.\ ", ".", last)
    last = re.sub(r"\d+\.\.\.", "", last)
    return last

traversal_tree(fake_move)

color = sys.argv[1]

def removeBadMoves(move):
    if move.evaluation in ["$4", "$2", "$6"]:
        return False
    return True

deviation = 1
for idx, fen in enumerate(fens):
    if len(list(filter(removeBadMoves, moves[idx].children))) > 1 and fen[-1] == color:
        print("-----deviation "+str(deviation)+"-----")
        deviation = deviation + 1
        for c in moves[idx].children:
            print(french_chess(c.str_to_root()))

for file in os.listdir(os.getcwd()):
    if file.endswith("_temp.pgn"):
        if os.path.exists(os.getcwd()+"\\"+file):
            os.remove(os.getcwd()+"\\"+file)
