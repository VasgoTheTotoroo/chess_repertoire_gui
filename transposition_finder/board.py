"""This module is the board of the window (only UI)"""

import os
import pickle
import random
from tkinter import Tk, Canvas, Event
import chess
import PIL.Image
import PIL.ImageTk

from utils import build_fen_dict, find_all_children, is_not_a_bad_move, move_full_print, traversal_tree

directory_path = os.path.abspath(os.path.dirname(__file__))

file_dict = {
    0: "a",
    1: "b",
    2: "c",
    3: "d",
    4: "e",
    5: "f",
    6: "g",
    7: "h"
}
rank_dict = {
    0: "8",
    1: "7",
    2: "6",
    3: "5",
    4: "4",
    5: "3",
    6: "2",
    7: "1"
}

reversed_file_dict = {v: k for k, v in file_dict.items()}
reversed_rank_dict = {v: k for k, v in rank_dict.items()}

eval_color = {
    "$1": "#749BBF",
    "$2": "#FFA459",
    "$3": "#26c2a3",
    "$4": "#FA412D",
    "$5": "#7979a1",
    "$6": "#F7C631",
}

class Board:
    """The board of the window"""

    def __init__(
        self,
        tk_window: Tk,
        base_length,
        master_window,
        init_nb_rows: int = 8,
        init_board_spacing: float = 0.05,
        black_square_color: str = "#C8AD7F",
        white_square_color: str = "#ffd791",
    ):
        self.nb_rows: int = init_nb_rows
        self.board_spacing: float = init_board_spacing
        self.black_square_color: str = black_square_color
        self.white_square_color: str = white_square_color
        self.white_color: str = "#FEFEE2"
        self.black_color: str = "#2F1E0E"
        self.master_window = master_window
        self.arrows = []
        self.board_flipped = False
        self.board_flipped_offset = self.nb_rows-1

        self.white_to_play = True
        self.chess_board = chess.Board()
        self.play_random = False
        self.repertoire_fens = []
        self.repertoire_moves = []
        self.transposition_dict = {}
        self.repertoire_loaded_moves = []
        self.player_color = "w"
        self.current_comments =[]

        self.board_position: float = base_length * self.board_spacing
        self.board_width: float = base_length * (1 - 2 * self.board_spacing)
        self.load_images()
        self.canvas: Canvas = Canvas(
            master=tk_window,
            width=self.board_width,
            height=self.board_width,
            bg="white",
        )
        self.canvas.place(
            x=base_length * self.board_spacing,
            y=base_length * self.board_spacing,
        )

    def update(self, base_length):
        """Update the board width and height and scale the drawing"""

        self.board_width: float = base_length * (1 - 2 * self.board_spacing)
        self.board_position: float = base_length * self.board_spacing

        self.canvas.config(
            width=self.board_width,
            height=self.board_width,
        )
        self.canvas.place(
            x=self.board_position,
            y=self.board_position,
        )
        self.load_images()
        self.draw()

    def bind(self):
        """Bind the events for the board"""

        # drag & drop the piece
        self.canvas.bind("<ButtonPress-1>", self.select_piece)
        self.canvas.bind("<Motion>", self.display_move_comment)

    def display_move_comment(self, event: Event):
        self.current_comments = []
        piece_x: int = event.x
        piece_y: int = event.y
        base_length: float = self.board_width / self.nb_rows
        init_piece_x_coord: int = int(piece_x / base_length)
        init_piece_y_coord: int = int(piece_y / base_length)
        arrow_ids = self.canvas.find_withtag(str(init_piece_x_coord)+"com"+str(init_piece_y_coord))
        tags = []
        moves_to_display_comment = []
        for id in arrow_ids:
            tags.append(self.canvas.itemcget(id, "tags"))
        for tag in tags:
            if len(tag) > 6:
                if tag[-1]=="t":
                    move_idx = tag[tag.find(" ")+1:tag.find(" ", tag.find(" ")+1)]
                else:
                    move_idx = tag[tag.find(" ")+1:]
                moves_to_display_comment.append(self.repertoire_moves[int(move_idx)])
        if len(moves_to_display_comment) < 1:
            self.current_comments = []
        else:
            self.update_comment_to_display(moves_to_display_comment)
        self.master_window.update_canvas(None)

    def select_piece(self, event: Event):
        """Select a piece to move"""

        piece_x: int = event.x
        piece_y: int = event.y
        base_length: float = self.board_width / self.nb_rows
        init_piece_x_coord: int = int(piece_x / base_length)
        init_piece_y_coord: int = int(piece_y / base_length)

        if (
            init_piece_x_coord > self.nb_rows - 1
            or init_piece_y_coord > self.nb_rows - 1
        ):
            return
        try:
            selected_piece: int = self.canvas.find_withtag(
            str(init_piece_y_coord) + ";" + str(init_piece_x_coord)
            )[0]
        except:
            return
        is_white: bool = (
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['P']) or 
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['R']) or 
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['B']) or 
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['N']) or 
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['Q']) or 
            self.canvas.itemcget(selected_piece, "image") == str(self.images_dict['K'])
        )
        
        if self.white_to_play and not is_white:
            return
        if not self.white_to_play and is_white:
            return

        def __internal_move_piece(
            event: Event,
            piece_id: int = selected_piece,
            init_coord: tuple[int, int] = (init_piece_x_coord, init_piece_y_coord),
            is_white = is_white,
        ):
            self.move_piece(
                event=event,
                piece_id=piece_id,
                init_coord=init_coord,
                is_white=is_white,
            )

        self.canvas.bind("<B1-Motion>", __internal_move_piece)

    def move_piece(
        self,
        event: Event,
        piece_id: int,
        init_coord: tuple[int, int],
        is_white,
    ):
        """Move the piece on the board"""

        new_x: float = event.x
        new_y: float = event.y

        # move the letter
        self.canvas.tag_raise(piece_id)
        self.canvas.coords(
            piece_id,
            new_x,
            new_y,
        )

        def __internal_drop_piece(
            event: Event,
            init_coord: tuple[int, int] = init_coord,
            is_white=is_white,
        ):
            self.drop_piece(event, init_coord, is_white)

        self.canvas.bind("<ButtonRelease-1>", __internal_drop_piece)

    def drop_piece(
        self, event: Event, init_coord: tuple[int, int], is_white
    ):
        """Drop the piece in the new square"""

        base_length: float = self.board_width / self.nb_rows
        new_piece_x_coord: int = int(event.x / base_length)
        new_piece_y_coord: int = int(event.y / base_length)
        # update the board, h8 is 7 0
        old_square = file_dict[init_coord[0]]+rank_dict[init_coord[1]]
        new_square = file_dict[new_piece_x_coord]+rank_dict[new_piece_y_coord]
        if self.board_flipped:
            old_square = file_dict[self.board_flipped_offset-init_coord[0]]+rank_dict[self.board_flipped_offset-init_coord[1]]
            new_square = file_dict[self.board_flipped_offset-new_piece_x_coord]+rank_dict[self.board_flipped_offset-new_piece_y_coord]
        uci_move = old_square+new_square
        if old_square.find(new_square) ==-1 and chess.Move.from_uci(uci_move) in self.chess_board.legal_moves:
            self.chess_board.push_uci(uci_move)
            self.white_to_play = not self.white_to_play
            if len(self.repertoire_loaded_moves) >0:
                try:
                    fen_idx = self.repertoire_fens.index(self.chess_board.fen()[:self.chess_board.fen().find(" ", self.chess_board.fen().find(" ")+1)])
                    self.repertoire_loaded_moves.append(self.repertoire_moves[fen_idx])
                    self.next_move(self.repertoire_moves[fen_idx], "b" if is_white else "w")
                except Exception:
                    pass

        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.master_window.update_canvas(None)

    def draw(
        self,
    ):
        """Draw the board with the pieces"""

        self.canvas.delete("all")

        base_length: float = self.board_width / self.nb_rows

        for i in range(0, self.nb_rows, 2):
            for j in range(0, self.nb_rows, 2):
                x_0: float = i * base_length
                y_0: float = j * base_length
                x_1: float = x_0 + base_length
                y_1: float = y_0 + base_length
                self.canvas.create_rectangle(
                    x_1, y_0, x_1 + base_length, y_1, fill=self.black_square_color
                )
                self.canvas.create_rectangle(
                    x_0, y_1, x_1, y_1 + base_length, fill=self.black_square_color
                )
                self.canvas.create_rectangle(
                    x_0, y_0, x_1, y_1, fill=self.white_square_color
                )
                self.canvas.create_rectangle(
                    x_1, y_1, x_1 + base_length, y_1 + base_length, fill=self.white_square_color
                )
                

        for i in range(self.nb_rows + 1):
            y_0: float = i * base_length
            for j in range(self.nb_rows + 1):
                x_0: float = j * base_length
                self.canvas.create_line(
                    x_0, 0, x_0, self.board_width, fill="black", width="1"
                )
                self.canvas.create_line(
                    0, y_0, self.board_width, y_0, fill="black", width="1"
                )
        #draw the file and rank number/letter
        for i in range(self.nb_rows):
            piece_idx = i
            if self.board_flipped:
                piece_idx = self.board_flipped_offset - i
            y_0: float = i * base_length
            self.canvas.create_text(
            y_0+0.9*base_length,
            self.board_width-0.15*base_length,
            font=("Arial", int(base_length * 0.2)),
            text=file_dict[piece_idx],
            )
            self.canvas.create_text(
            0.15*base_length,
            y_0+0.15*base_length,
            font=("Arial", int(base_length * 0.2)),
            text=rank_dict[piece_idx],
            )
        # draw the pieces
        for i in range(0, self.nb_rows):
            x_idx = i
            if self.board_flipped:
                x_idx=self.nb_rows-1-i
            for j in range(0, self.nb_rows):
                y_idx = j
                if self.board_flipped:
                    y_idx=self.nb_rows-1-j
                x_0: float = x_idx * base_length
                y_0: float = y_idx * base_length
                piece_to_draw = self.chess_board.__str__().replace(" ", "").replace("\n", "")[(j*self.nb_rows)+i]
                self.draw_piece(
                    x_0=x_0,
                    y_0=y_0,
                    piece=piece_to_draw,
                    base_length=base_length,
                    square_tag=str(y_idx) + ";" + str(x_idx),
                )
        self.draw_arrows()

    def draw_piece(
        self, x_0: float, y_0: float, piece: str, base_length: float, square_tag: str
    ):
        """Draw the pieces on the board"""

        base_length_50: float = base_length / 2
        if piece != ".":
            self.canvas.create_image(x_0 + base_length_50, y_0 + base_length_50, image=self.images_dict[piece], tags=square_tag)
    
    def draw_arrows(self):
        base_length: float = self.board_width / self.nb_rows
        for arrow in self.arrows:
            base_length_50 = base_length / 2
            file_idx_start_arrow = reversed_file_dict[arrow[0]]
            rank_idx_start_arrow = reversed_rank_dict[arrow[1]]
            if self.board_flipped:
                file_idx_start_arrow = self.board_flipped_offset - reversed_file_dict[arrow[0]]
                rank_idx_start_arrow = self.board_flipped_offset - reversed_rank_dict[arrow[1]]
                x1 = ((self.board_flipped_offset - reversed_file_dict[arrow[2]]) * base_length) + base_length_50
                y1 = ((self.board_flipped_offset - reversed_rank_dict[arrow[3]]) * base_length) + base_length_50
            else:
                x1 = ((reversed_file_dict[arrow[2]]) * base_length) + base_length_50
                y1 = ((reversed_rank_dict[arrow[3]]) * base_length) + base_length_50
            x0 = (file_idx_start_arrow * base_length) + base_length_50
            y0 = (rank_idx_start_arrow * base_length) + base_length_50
            fill="#000000" if arrow[4]=="1" else "#949494"
            width=13 if arrow[4]=="1" else 5
            move = self.repertoire_moves[int(arrow[5:])]
            if move.evaluation:
                for eval in move.evaluation:
                    if eval in list(eval_color.keys()):
                        fill = eval_color[eval]
                        break
            self.canvas.create_line(x0, y0, x1, y1, arrow="last", width=width, fill=fill, tags=[str(file_idx_start_arrow)+"com"+str(rank_idx_start_arrow), arrow[5:]])

    def load_images(self):
        """Load the images and save it to the board object images_dict"""
        base_length: float = self.board_width / self.nb_rows
        images_dict = {}
        for file in os.listdir(directory_path+r"\images\pieces"):
                if file.endswith(".png"):
                    full_path_file = directory_path+r"\images\pieces\\"+file
                    image_file = PIL.Image.open(full_path_file)
                    image_file = image_file.resize((int(base_length),int(base_length)))
                    piece = file[1] if file[0]=="b" else file[1].upper()
                    images_dict[piece] = PIL.ImageTk.PhotoImage(image_file)
        self.images_dict = images_dict
    
    def switch_random(self):
        self.play_random = not self.play_random
    
    def choose_color(self, b_or_w):
        with open(os.path.join(directory_path+r"\repertoire\\", b_or_w+'.repertoire.pickle'), 'rb') as handle:
            self.repertoire_loaded_moves.append(pickle.load(handle))
        traversal_tree(self.repertoire_loaded_moves[-1], self.repertoire_fens, self.repertoire_moves)
        self.board_flipped = b_or_w =="b"
        self.master_window.update_canvas(None)
        
        self.transposition_dict = build_fen_dict(self.repertoire_fens)
        self.player_color = b_or_w
        self.next_move(self.repertoire_loaded_moves[-1], b_or_w)
    
    def update_comment_to_display(self, moves):
        for move in moves:
            string = move_full_print(move)
            if string not in self.current_comments:
                font_color = "#000000"
                if move.evaluation:
                    for eval in move.evaluation:
                        if eval in list(eval_color.keys()):
                            font_color = eval_color[eval]
                self.current_comments.append((move_full_print(move), move.main_variant, font_color))

    def next_move(self, move, b_or_w):
        self.arrows=[]
        self.draw_arrows()

        self.update_comment_to_display([move])

        #we know the color of the first_move
        if move.fen!="w ":
            color = move.fen[move.fen.find(" ")+1]
        else:
            color = "w"
        
        new_move = move
        if color == b_or_w and self.play_random and self.player_color == color:
            idx = self.repertoire_moves.index(move)
            all_children = find_all_children(self.transposition_dict, self.repertoire_fens[idx], self.repertoire_moves, idx, False)
            #pick a random move
            random_move = random.choice(list(filter(is_not_a_bad_move, all_children)))
            new_move = random_move
            self.repertoire_loaded_moves.append(new_move)
            self.chess_board.push_san(new_move.name[new_move.name.find(" ")+1:])
            self.white_to_play = not self.white_to_play
            self.draw()
        
        idx = self.repertoire_moves.index(new_move)
        all_children = find_all_children(self.transposition_dict, self.repertoire_fens[idx], self.repertoire_moves, idx, False)
        for c in all_children:
            test_fen = c.fen[:c.fen.find(" ", c.fen.find(" ")+1)]
            move_idx = self.repertoire_moves.index(c)
            if test_fen in self.transposition_dict.keys():
                for concurent_move_idx in self.transposition_dict[test_fen]:
                    if self.repertoire_moves[concurent_move_idx].name == c.name:
                        move_idx = concurent_move_idx
                        break
            uci_move = self.chess_board.parse_san(c.name[c.name.find(" ")+1:]).__str__()
            main_var = "1" if c.main_variant else "0"
            self.arrows.append(uci_move+main_var+str(move_idx))
        self.draw_arrows()
    
    def take_back_last(self):
        self.white_to_play = not self.white_to_play
        self.chess_board.pop()
        self.repertoire_loaded_moves.pop()
        self.next_move(self.repertoire_loaded_moves[-1], "w" if self.white_to_play else "b")
        self.current_comments = []
        self.master_window.update_canvas(None)
        
    def reset_game(self):
        self.white_to_play = True
        self.chess_board = chess.Board()
        self.play_random = False
        self.repertoire_fens = []
        self.repertoire_moves = []
        self.transposition_dict = {}
        self.repertoire_loaded_moves = []
        self.arrows = []
        self.player_color = "w"
        self.board_flipped = False
        self.current_comments=[]
        self.master_window.update_canvas(None)
    
    def flip_board(self):
        self.board_flipped = not self.board_flipped
        self.master_window.update_canvas(None)