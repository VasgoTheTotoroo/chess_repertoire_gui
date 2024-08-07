"""This module implement the Window class"""

from tkinter import Tk
from background import Background
from board import Board


class Window:
    """The window of the game"""

    def __init__(
        self,
        init_width: int = 1700,
        init_height: int = 800,
        init_x: int = 0,
        init_y: int = 0,
    ):
        """Init the window with Parameters:
        init_width (int): the width of the window
        init_height (int): the height of the window
        """

        self.window: Tk = Tk()
        self.init_window(
            init_width=init_width, init_height=init_height, init_x=init_x, init_y=init_y
        )

        if init_width > init_height:
            base_length: int = init_height
        else:
            base_length: int = init_width

        self.background: Background = Background(
            tk_window=self.window,
            init_width=init_width,
            init_height=init_height,
            base_length=base_length,
            master_window=self,
        )

        self.board: Board = Board(
            tk_window=self.window,
            base_length=base_length,
            master_window=self,
        )

        self.bind_events()

        self.window.mainloop()

    def init_window(self, init_width: int, init_height: int, init_x: int, init_y: int):
        """Init the main Tinker window"""

        self.window.geometry(
            newGeometry=str(init_width)
            + "x"
            + str(init_height)
            + "+"
            + str(init_x)
            + "+"
            + str(init_y)
        )
        self.window.title("Chess")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    def update_canvas(self, _):
        """Update all the canvas when the window is resizing"""

        window_width: int = self.window.winfo_width()
        window_height: int = self.window.winfo_height()

        if window_width > window_height:
            self.base_length: int = window_height
        else:
            self.base_length: int = window_width

        self.background.update(
            window=self.window,
            play_random=self.board.play_random,
            board_width=self.board.board_width,
            board_position=self.board.board_position,
        )
        self.board.update(base_length=self.base_length)

    def bind_events(self):
        """Bind the events to the fcts for the different canvas"""

        self.window.bind("<Configure>", self.update_canvas)
        self.board.bind()
