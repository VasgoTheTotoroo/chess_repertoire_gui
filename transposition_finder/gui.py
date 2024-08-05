import pickle
import tkinter as tk
import random
from functools import partial
import os
from utils import *

random_activated = False

eval_color = {
    "$1": "#749BBF",
    "$2": "#FFA459",
    "$3": "#26c2a3",
    "$4": "#FA412D",
    "$5": "#7979a1",
    "$6": "#F7C631",
}

def reset_window_elements(window):
    window_elements = window.grid_slaves()
    for l in window_elements:
        l.destroy()
    canvas = tk.Canvas(window)
    canvas.grid()
    return canvas

def choose_color(b_or_w, window):
    with open(os.path.join(r"C:\Users\vassia\Desktop\echec\transposition_finder\repertoire\\", b_or_w+'.repertoire.pickle'), 'rb') as handle:
        fake_move = pickle.load(handle)
    fens = []
    moves = []
    traversal_tree(fake_move, fens, moves)
    
    D = build_fen_dict(fens)
    next_move(window, fake_move, moves, fens, D, b_or_w)

def switch_random(window):
    global random_activated
    random_activated = not random_activated
    reset_window_elements(window)
    reset_game(window)

def reset_game(window):
    global random_activated
    canvas = reset_window_elements(window)
    
    tk.Button(canvas, text="WHITE", width=40, height=6, font=("Arial", 15), command=partial(choose_color, "w", window)).grid(column=0, row=0)
    tk.Button(canvas, text="BLACK", width=40, height=6, font=("Arial", 15), command=partial(choose_color, "b", window)).grid(column=0, row=1)
    tk.Button(canvas, text="RANDOM is "+str(random_activated), width=40, height=6, font=("Arial", 15), fg="#eb4034" if not random_activated else "#34eb77", command=partial(switch_random, window)).grid(column=0, row=3)
        
def next_move(window, move, moves, fens, D, b_or_w):
    canvas = reset_window_elements(window)
    
    #we know the color of the first_move
    if move.fen!="w ":
        color = move.fen[move.fen.find(" ")+1]
    else:
        color = "w"
    
    idx = moves.index(move)
    all_children = find_all_children(D, fens[idx], moves, idx, False)
    
    if color == b_or_w and random_activated:
        #pick a random move
        random_move = random.choice(list(filter(is_not_a_bad_move, all_children)))
        move = random_move
        tk.Label(canvas, text = "You need to play "+move_full_print(random_move), bd =0, wraplength=250, width=30, height=8, font=("Arial", 15, "bold")).grid(column=0, row=6, columnspan=4)
    
    idx = moves.index(move)
    all_children = find_all_children(D, fens[idx], moves, idx, False)
    
    if len(all_children) == 0:
        tk.Label(canvas, text = "You are outside of your repertoire !", font=("Arial", 25)).grid()
        tk.Button(canvas, text="RESET", width=40, height=6, font=("Arial", 15), command=partial(reset_game, window)).grid()
    for i, c in enumerate(all_children):
        font = ("Arial", 11, "bold") if c.main_variant else ("Arial", 12, "normal")
        font_color = "#000000"
        if c.evaluation:
            for eval in c.evaluation:
                if eval in list(eval_color.keys()):
                    font_color = eval_color[eval]
        tk.Button(canvas, text=move_full_print(c), bd =5, padx=1, fg=font_color, pady=1, wraplength=250, width=30, height=8, font=font, command=partial(next_move, window, c, moves, fens, D, b_or_w)).grid(column=i%4, row=i//4)