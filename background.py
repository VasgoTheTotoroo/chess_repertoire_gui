"""This module is the background of the window"""

import os
from tkinter import Button, Label, Tk, Canvas, Text
from functools import partial
import PIL.Image
import PIL.ImageTk

from utils import move_full_print

directory_path = os.path.abspath(os.path.dirname(__file__))

eval_color = {
    "$1": "#749BBF",
    "$2": "#FFA459",
    "$3": "#26c2a3",
    "$4": "#FA412D",
    "$5": "#7979a1",
    "$6": "#F7C631",
}


class Background:
    """The background of the window"""

    def __init__(
        self,
        tk_window: Tk,
        init_width: int,
        init_height: int,
        base_length,
        master_window,
        init_background_color: str = "#4E3D28",
    ):
        self.canvas: Canvas = Canvas(
            master=tk_window,
            width=init_width,
            height=init_height,
            bg=init_background_color,
        )
        self.canvas.place(x=0, y=0)
        self.base_length = base_length
        self.master_window = master_window
        self.random_move_btn = Button(
            self.canvas,
            text="RANDOM is " + str(False),
            width=15,
            height=2,
            font=("Arial", 10),
            fg="#eb4034",
            command=partial(self.switch_random),
        )
        self.white_button = Button(
            self.canvas,
            text="WHITE",
            width=15,
            height=2,
            font=("Arial", 10),
            command=partial(self.switch_to_white_repertoire),
        )
        self.black_button = Button(
            self.canvas,
            text="BLACK",
            width=15,
            height=2,
            font=("Arial", 10),
            command=partial(self.switch_to_black_repertoire),
        )
        self.reset_button = Button(
            self.canvas,
            text="RESET",
            width=15,
            height=2,
            font=("Arial", 10),
            command=partial(self.reset_game),
        )
        self.take_back_button = Button(
            self.canvas,
            text="Take back last move",
            width=15,
            height=2,
            font=("Arial", 10),
            state="disabled",
            command=partial(self.take_back_move),
        )

        image_file = PIL.Image.open(directory_path + r"\images\flip.png")
        image_file = image_file.resize((17, 17))
        self.flip_img = PIL.ImageTk.PhotoImage(image_file)  # keep a reference!
        self.flip_button = Button(
            self.canvas,
            image=self.flip_img,  # type: ignore
            command=partial(self.flip_board),
        )

        self.last_move = Label(
            self.canvas,
            text="",
            bd=0,
            wraplength=700,
            width=90,
            height=4,
            background="#ffe6bd",
            font=("Arial", 10),
        )
        self.comments = []
        for _ in range(8):
            self.comments.append(
                Label(
                    self.canvas,
                    text="",
                    bd=0,
                    wraplength=700,
                    width=90,
                    height=4,
                    font=("Arial", 10),
                )
            )
        self.save_repertoire = Button(
            self.canvas,
            text="save to repertoire",
            width=15,
            height=2,
            font=("Arial", 10),
            state="disabled",
            command=partial(self.save_to_repertoire),
        )
        self.move_eval_box = Text(
            self.canvas,
            width=8,
            height=2,
            font=("Arial", 10),
        )
        self.move_eval_send = Button(
            self.canvas,
            text="modify move evaluation",
            width=9,
            height=2,
            wraplength=100,
            font=("Arial", 10),
            command=partial(self.send_eval),
        )
        self.new_file = Button(
            self.canvas,
            text="move in a new file (to do after)",
            width=9,
            height=2,
            wraplength=70,
            font=("Arial", 10),
            command=partial(self.new_file_for_last_move),
        )

        self.delete_move = Button(
            self.canvas,
            text="delete last move from repertoire",
            width=15,
            height=2,
            font=("Arial", 10),
            state="normal",
            wraplength=100,
            command=partial(self.delete_latest_move),
        )

        self.stockfish = Label(
            self.canvas,
            text="",
            bd=0,
            wraplength=900,
            width=110,
            height=8,
            font=("Arial", 10),
        )

        self.compute_stockfish = Button(
            self.canvas,
            text="compute stockfish",
            width=15,
            height=2,
            font=("Arial", 10),
            state="normal",
            wraplength=100,
            command=partial(self.compute_stockfish_score),
        )

    def update(self, window: Tk, play_random, board_width, board_position):
        """Update the background width and height"""

        self.canvas.config(width=window.winfo_width(), height=window.winfo_height())

        self.random_move_btn.config(
            text="RANDOM is " + str(play_random),
            fg="#eb4034" if not play_random else "#34eb77",
        )
        self.random_move_btn.place(
            x=board_width + board_position + 50, y=board_position
        )

        self.white_button.place(x=board_width + board_position + 225, y=board_position)
        self.black_button.place(x=board_width + board_position + 400, y=board_position)
        self.reset_button.place(x=board_width + board_position + 575, y=board_position)
        self.take_back_button.place(
            x=board_width + board_position + 750, y=board_position
        )
        self.flip_button.place(x=board_width + board_position + 10, y=board_position)

        self.save_repertoire.place(x=board_width + board_position + 50, y=board_width)
        self.move_eval_box.place(x=board_width + board_position + 225, y=board_width)
        self.move_eval_send.place(x=board_width + board_position + 300, y=board_width)
        self.new_file.place(x=board_width + board_position + 400, y=board_width)
        self.delete_move.place(x=board_width + board_position + 500, y=board_width)
        self.compute_stockfish.place(
            x=board_width + board_position + 650, y=board_width
        )

        self.stockfish.place(x=board_width + board_position + 50, y=board_width - 140)

        if (
            len(self.master_window.board.repertoire_loaded_moves) > 0
            and self.master_window.board.repertoire_loaded_moves[-1].name != ""
        ):
            last_move = self.master_window.board.repertoire_loaded_moves[-1]
            font_color = "#000000"
            if last_move.evaluation:
                for chess_eval in last_move.evaluation:
                    if chess_eval in list(eval_color):
                        font_color = eval_color[chess_eval]
            if last_move.main_variant:
                font = ("Arial", 10, "bold")
            else:
                font = ("Arial", 10, "normal")
            self.last_move.config(
                text=move_full_print(last_move), fg=font_color, font=font
            )
            self.last_move.place(
                x=board_width + board_position + 50, y=board_position + 75
            )
        else:
            self.last_move.place_forget()

        for i, comment in enumerate(self.comments):
            if len(self.master_window.board.current_comments) > i:
                comment.config(text=self.master_window.board.current_comments[i][0])
                comment["fg"] = self.master_window.board.current_comments[i][2]
                if self.master_window.board.current_comments[i][1]:
                    comment["font"] = ("Arial", 10, "bold")
                else:
                    comment["font"] = ("Arial", 10, "normal")
                comment.place(
                    x=board_width + board_position + 50, y=board_position + 150 + 75 * i
                )
            else:
                comment.place_forget()

        if (
            self.master_window.board.chess_board.fen()
            != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        ):
            self.black_button["state"] = "disabled"
            self.white_button["state"] = "disabled"

            self.save_repertoire["state"] = "normal"
            self.take_back_button["state"] = "normal"
        else:
            self.black_button["state"] = "normal"
            self.white_button["state"] = "normal"

            self.save_repertoire["state"] = "disabled"
            self.take_back_button["state"] = "disabled"

    def switch_random(self):
        self.master_window.board.switch_random()
        self.master_window.update_canvas(None)

    def switch_to_white_repertoire(self):
        self.master_window.board.choose_color("w")

    def switch_to_black_repertoire(self):
        self.master_window.board.choose_color("b")

    def reset_game(self):
        self.master_window.board.reset_game()

    def take_back_move(self):
        self.master_window.board.take_back_last()

    def flip_board(self):
        self.master_window.board.flip_board()

    def save_to_repertoire(self):
        self.master_window.board.save_to_repertoire()

    def send_eval(self):
        move_eval = self.move_eval_box.get(1.0, "end")
        self.master_window.board.modify_last_move_eval(move_eval[:-1])
        self.move_eval_box.delete(1.0, "end")

    def new_file_for_last_move(self):
        self.master_window.board.new_file_for_last_move()

    def delete_latest_move(self):
        self.master_window.board.take_back_last(True)

    def compute_stockfish_score(self):
        score = self.master_window.board.get_position_score()
        self.stockfish.config(text=score)
