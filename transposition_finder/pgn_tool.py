from move import *
from utils import *
from gui import *
import tkinter as tk
import textwrap
import csv
from window import Window

# C:\Users\vassia\Desktop\echec\chess_repertoire_gui\transposition_finder\pgn_tool.py

while True:
    directory_path = os.path.abspath(os.path.dirname(__file__))
    use = input("What do you want to do?\n[1]find transpositions\n[2]find all of your deviation\n[3]split pgns exported with chessbase\n[4]save your repertoire to a file\n[5]play a game (text) DEPRECATED\n[6]Fill opening names\n[7]Play a game (GUI)\n")

    if use == "1":
        fake_move = read_and_build_tree()
        
        fens = []
        moves = []
        traversal_tree(fake_move, fens, moves)

        D = build_fen_dict(fens)
        D = list(D.values())

        true_duplicates=[]
        for d in D:
            nb_comments = 0
            for idx in d:
                if moves[idx].comments is not None:
                    if moves[idx].comments.find("Transposition") > -1:
                        nb_comments+=1
                if moves[idx].parent.comments is not None:
                    if moves[idx].parent.comments.find("Transposition") > -1:
                        nb_comments+=1
                if len(moves[idx].children) > 0:
                    for move in moves[idx].children:
                        if move.comments:
                            if move.comments.find("Transposition") > -1:
                                nb_comments+=1
            if nb_comments < len(d)-1:
                true_duplicates.append(d)

        print(true_duplicates)

        for i, duplication in enumerate(reversed(true_duplicates)):
            strings = []
            for idx in duplication:
                strings.append("Transposition "+french_chess(moves[idx].str_to_root()))
            # Remove mates and draw repetition moves
            if strings[1].find(strings[0]) > -1 or strings[0][-1] == "#":
                # print("REPETITION OR MATE")
                # for s in strings:
                #     print(s)
                pass
            elif len(strings) > 2 and strings[2].find(strings[0]) > -1:
                pass
            else:
                print("duplication "+str(i)+":\n")
                for s in strings:
                    print(s)
                print("\n")

    elif use=="2":
        fake_move = read_and_build_tree()
        fens = []
        moves = []
        traversal_tree(fake_move, fens, moves)
        
        D = build_fen_dict(fens)
        
        color = input("Which color do you want to find deviation for?[w/b]\n")
        if color !="w" and color !="b":
            print("I don't know this color!")
        else:
            deviation = 1
            for idx, fen in enumerate(fens):
                all_children = find_all_children(D, fen, moves, idx, True)
                if len(fen)>0 and len(list(filter(is_not_a_bad_move, all_children))) > 1 and fen[-1] == color:
                    print("-----deviation "+str(deviation)+"-----")
                    deviation = deviation + 1
                    for c in all_children:
                        print(french_chess(c.str_to_root())+(" "+c.comments if c.comments else ""))

    elif use == "3":
        # file_name = input("What is the file name?\n")
        file = open(directory_path+r"\pgns\game1.pgn", encoding="utf-8")
        file_str = file.read().split("[Event \"")

        for i, s in enumerate(file_str[1:]):
            idx_name = s.find("[White")+8
            splitted_file = "\n".join(textwrap.wrap(s[s.find("\n\n"):], 70))
            color_name = "White"
            if s[idx_name] == "?":
                # We take for name of the file what is between the Black square brackets in the pgn if there is nothing in the White
                color_name = "Black"
            file_name = "("+str(i+1)+") "+s[s.find("["+color_name)+8:s.find("\"", s.find("["+color_name)+8)]+".pgn"
            print(file_name)
            f = open(os.path.join(directory_path+r"\pgns\\", file_name), "w",  encoding="utf-8")
            f.write(s[:s.find("\n\n")+2]+splitted_file)
            f.close()
        file.close()

    elif use == "4":
        fake_move = read_and_build_tree()
        b_or_w = input("save it as black or white repertoire?[w/b]\n")
        with open(os.path.join(directory_path+r"\repertoire\\", b_or_w+'.repertoire.pickle'), 'wb') as handle:
            pickle.dump(fake_move, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("repertoire saved!")

    elif use == "5":
        window = tk.Tk()
        window.title('échecs')
        window.geometry('1200x950')
        window.protocol("WM_DELETE_WINDOW", lambda : window.destroy())
        
        reset_game(window)
        
        window.mainloop()
    
    elif use == "6":
        eco_codes=[]
        for file in os.listdir(directory_path+r"\chess-openings"):
            full_path_file = directory_path+r"\chess-openings\\"+file
            tab_file = open(full_path_file, encoding="utf-8")
            tsv_file = csv.reader(tab_file, delimiter="\t")
            for line in tsv_file:
                if line[0]!="eco":
                    truncated_fen = line[4][0:line[4].find(" ")+2]
                    eco_codes.append([line[1], truncated_fen])
            tab_file.close()
        
        for file in os.listdir(directory_path+r"\pgns"):
            fake_move = Move("", fen="w ")
            full_path_file = directory_path+r"\pgns\\"+file
            if file.endswith(".pgn") and file != "game1.pgn":
                subprocess.check_call([directory_path+r"\pgn-extract.exe", "-F", "--fencomments", full_path_file, "-o", full_path_file+"_temp.pgn"])

                temp_pgn = open(full_path_file+"_temp.pgn", "r", encoding="utf-8")
                fen_pgn = temp_pgn.read().replace('\n', ' ')
                temp_pgn.close()
                fen_pgn = re.sub(r"\( \d+\.", lambda match: match.group(0).replace(" ",""), fen_pgn)
                for opening in eco_codes:
                    fen_idx = fen_pgn.find(opening[1])
                    if fen_idx!=-1:
                        # if there is no comment already on the move
                        if fen_pgn[fen_idx-4] != "}":
                            fen_pgn = fen_pgn[:fen_idx-3]+" { "+opening[0]+" }"+fen_pgn[fen_idx-3:]
                        else:
                            fen_pgn = fen_pgn[:fen_idx-4]+opening[0]+" "+fen_pgn[fen_idx-4:]
                fen_pgn = re.sub(r"(?<=\{)[^}]*\/+[^}]*(?=\})", "", fen_pgn)
                fen_pgn = fen_pgn.replace("{}","").replace("]", "]\n")
                write_pgn = open(full_path_file, "w", encoding="utf-8")
                write_pgn.write(fen_pgn)
                write_pgn.close()
        remove_temp_pgn()
    elif use == "7":
        # possible improvment :
        #   - rotate the board if we play Black
        #   - put everything under the gui
        Window()
    else:
        print("I don't understand what you want to do, I quit!")
        break
    print("\n")