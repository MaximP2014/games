#!/usr/bin/python3
# Tetravex Game
#
#
# Copyright (C) 2022 Maksim Petrenko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Tetravex Game"""


# Standard library
#import concurrent.futures
import tkinter
from tkinter import ttk
import random


# Constants
INFO = "\
Tetravex is a simple puzzle where pieces must be positioned so \
that the same edges are touching each other."
SIZE = 3 # 3x3 tables
# From coordinates to cells
L_BOARD = {(4, 4, 104, 104): (0, 0),
           (112, 4, 212, 104): (0, 1),
           (220, 4, 320, 104): (0, 2),
           (4, 112, 104, 212): (1, 0),
           (112, 112, 212, 212): (1, 1),
           (220, 112, 320, 212): (1, 2),
           (4, 220, 104, 320): (2, 0),
           (112, 220, 212, 320): (2, 1),
           (220, 220, 320, 320): (2, 2)}
# Coordinates
R_BOARD = ((377, 4, 477, 104), (485, 4, 585, 104), (593, 4, 693, 104),
           (377, 112, 477, 212), (485, 112, 585, 212), (593, 112, 693, 212),
           (377, 220, 477, 320), (485, 220, 585, 320), (593, 220, 693, 320))
COLORS = ("black",
          "red",
          "orange",
          "yellow",
          "green",
          "brown",
          "light blue",
          "dark blue",
          "purple")
TILE = {"north": None,
        "east": None,
        "south": None,
        "west": None}
FONT = "DejaVu Sans"


# Globals
board = {}
tiles = {}


########################################################################
# BACKEND


# Functions

def triangles(x0=0, y0=0, xn=0, yn=0):
    """Return 4 triangles coordinates."""
    return ((x0, y0, x0+50, y0+50, xn, y0), # top
            (xn, y0, x0+50, y0+50, xn, yn), # right
            (xn, yn, x0+50, y0+50, x0, yn), # bottom
            (x0, yn, x0+50, y0+50, x0, y0)) # left


def make_tiles():
    """Make new tiles dict."""
    global tiles
    # Table
    temp_board = {(x, y): TILE.copy() for (x, y) in L_BOARD.values()}
    # x - row
    # y - column
    for x in range(SIZE+1):
        for y in range(SIZE):
            color = random.choice(COLORS)
            if x >= 1:
                temp_board[x-1, y]["south"] = color
            if x < SIZE:
                temp_board[x, y]["north"] = color
    for x in range(SIZE):
        for y in range(SIZE+1):
            color = random.choice(COLORS)
            if y >= 1:
                temp_board[x, y-1]["east"] = color
            if y < SIZE:
                temp_board[x, y]["west"] = color
    tiles = {f"tile{i}": j for (i, j) in enumerate(temp_board.values(), 1)}


def check_field(coords=[], tile=""):
    """Check field to move."""
    (x, y) = L_BOARD[tuple(coords)]
    # Top
    if board.get((x-1, y)) and board.get((x-1, y)) != tile:
        if tiles[board[x-1, y]]["south"] != tiles[tile]["north"]:
            return False
    # Right
    if board.get((x, y+1)) and board.get((x, y+1)) != tile:
        if tiles[board[x, y+1]]["west"] != tiles[tile]["east"]:
            return False
    # Bottom
    if board.get((x+1, y)) and board.get((x+1, y)) != tile:
        if tiles[board[x+1, y]]["north"] != tiles[tile]["south"]:
            return False
    # Left
    if board.get((x, y-1)) and board.get((x, y-1)) != tile:
        if tiles[board[x, y-1]]["east"] != tiles[tile]["west"]:
            return False
    return True


def update_board(tile="", coords=[]):
    """Update board dict."""
    global board
    if tile in board.values():
        cell = [k for k, v in board.items() if v == tile]
        board.pop(*cell)
    if tuple(coords) in L_BOARD:
        (x, y) = L_BOARD[tuple(coords)]
        board[x, y] = tile


########################################################################
# FRONTEND


class MainWindow(tkinter.Tk):
    """Game main window."""

    def __init__(self):
        super().__init__()
        # Window manager
        self.title("* Tetravex *")
        self.geometry("+{}+{}".format(self.winfo_screenwidth() // 2 - 357,
                                      self.winfo_screenheight() // 2 - 171))
        self.resizable(False, False)
        # Data
        self.sel_tile = {}
        self.sel_field = {}
        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=(FONT, 42, "bold"))
        # Widgets
        self.frame = ttk.Frame(self)
        self.frame.pack(padx=8, pady=8)
        # Canvas
        self.canvas = tkinter.Canvas(self.frame, width=697, height=324)
        self.canvas.pack()
        # Items
        # Fields 100x100
        for (i, coords) in enumerate(L_BOARD, start=1):
            self.canvas.create_rectangle(coords, fill="grey",
                                         tags=("fields", f"field{i}"))
        # Arrow
        self.canvas.create_polygon((336, 162, 361, 66, 361, 258), fill="grey",
                                   tags=("arrow"))
        # Tiles 100x100
        for (i, coords) in enumerate(R_BOARD, start=1):
            for (tcoords, s) in zip(triangles(*coords), TILE):
                self.canvas.create_polygon(tcoords, tags=("tiles", f"tile{i}",
                                                          f"tile{i}.{s}"))
        # Bindings
        self.canvas.tag_bind("fields", "<Enter>",
            lambda e: self.canvas.itemconfig("current", fill="dark grey"))
        self.canvas.tag_bind("fields", "<Leave>",
            lambda e: self.canvas.itemconfig("current", fill="grey"))
        self.canvas.tag_bind("fields", "<ButtonPress-1>", self.move)
        self.canvas.tag_bind("tiles", "<ButtonPress-1>", self.move)
        # Message
        self.canvas.create_rectangle((377, 4, 693, 320), fill=self.cget("bg"),
                                     tags=("message"))
        self.canvas.create_text(535, 54, text="\uFFFD",
                                font=(FONT, 64, "normal"), tags=("message"))
        self.canvas.create_text(535, 162, text=INFO, width=300,
                                font=(FONT, 14, "normal"), tags=("message"))
        # Button
        self.playbtn = ttk.Button(self.frame, text="\u21AA", command=self.play)
        self.playbtn.place(x=495, y=230, width=80, height=80)

    def play(self):
        """Play new game."""
        global board, tiles
        board = {}
        tiles = {}
        if self.canvas.gettags("mark"):
            self.canvas.delete("mark")
        self.playbtn.place_forget()
        if self.playbtn.cget("text") == "\u21AA":
            self.playbtn.config(text="\u27F3")
        self.canvas.delete("message")
        # New board
        for (i, coords) in enumerate(L_BOARD, start=1):
            self.canvas.moveto(f"field{i}", coords[0]-1, coords[1]-1)
        make_tiles()
        r_board = list(R_BOARD)
        random.shuffle(r_board)
        for (tile, coords) in zip(tiles, r_board):
            self.canvas.moveto(tile, coords[0]-1, coords[1]-1)
            for s in TILE:
                self.canvas.itemconfig(f"{tile}.{s}", fill=tiles[tile][s])

    def move(self, event):
        """Move tile."""
        tags = self.canvas.gettags("current")
        # Select tile
        if "tiles" in tags:
            if self.sel_tile:
                self.canvas.delete("mark")
            self.sel_tile = {"tag": tags[1],
                             "coords": self.canvas.bbox(tags[1])}
            # Mark
            self.canvas.create_text(self.sel_tile["coords"][0]+51,
                                    self.sel_tile["coords"][1]+51,
                                    text="\u2738", font=(FONT, 60, "normal"),
                                    fill="white", tags=("mark"))
        # Select field
        if "fields" in tags and self.sel_tile:
            self.sel_field = {"tag": tags[1],
                              "coords": self.canvas.coords(tags[1])}
            # Check field
            if tuple(self.sel_field["coords"]) in L_BOARD:
                if not check_field(self.sel_field["coords"],
                                   self.sel_tile["tag"]):
                    self.sel_field = {}
        # Switch
        if self.sel_tile and self.sel_field:
            self.canvas.delete("mark")
            self.canvas.moveto(self.sel_tile["tag"],
                               self.sel_field["coords"][0]-1,
                               self.sel_field["coords"][1]-1)
            self.canvas.moveto(self.sel_field["tag"],
                               *self.sel_tile["coords"][:2])
            update_board(self.sel_tile["tag"], self.sel_field["coords"])
            self.sel_tile = {}
            self.sel_field = {}
            # Check solving
            if self.canvas.bbox("tiles") == (3, 3, 321, 321):
                # Message
                self.canvas.create_rectangle((377, 4, 693, 320),
                                             fill=self.cget("bg"),
                                             tags=("message"))
                self.canvas.create_text(535, 54, text="\u263A",
                                        font=(FONT, 64, "normal"),
                                        tags=("message"))
                self.canvas.create_text(535, 162, text="Congratulations!",
                                        width=300, font=(FONT, 16, "bold"),
                                        tags=("message"))
                self.playbtn.place(x=495, y=230, width=80, height=80)


########################################################################
# EXECUTION


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()

