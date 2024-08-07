# chess_repertoire_gui
A project that was first about finding moves transposition across different files and now about building a GUI to have fun with your own repertoire.

You need to download [pgn-extract](https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/) and put the .exe file in the root directory along with the .py files if you want to use all the features of the repertoire reader and building.

## Use
1. gather your pgn files that build your repertoire. You can do it by exporting all of your pgn files into one through ChessBase.
2. If you exported your files into one through ChessBase, you need to put this file into **chess_repertoire_gui/pgns** and execute `chess_repertoire_gui/pgn_tool.py split_pgn`. It will split all of the pgns that are inside the ChessBase exported one.
3. Now, you can execute `chess_repertoire_gui/pgn_tool.py find_transpositions` to find all the transpositions in and between the files.
4. You can also execute `chess_repertoire_gui/pgn_tool.py find_deviations` to find all the different variantes you have on this repertoire.
5. You can save your repertoire with the command `chess_repertoire_gui/pgn_tool.py save_to_repertoire`. It will save the pgns you have in the **chess_repertoire_gui/pgns** folder into **chess_repertoire_gui/repertoire/[w/b].repertoire.picke** with the good data format for the program.
6. (Bonus) You can fill your pgns with the opening names on each move where it finds it with `chess_repertoire_gui/pgn_tool.py fill_opening_names`
7. You can then start the main GUI by clicking on pgn_tools.py or launching it via command line. If you click on the White or Black button, it will load the corresponding repertoire you have saved previously. The random option will pick one random move from your repertoire that is not flagged with a ?, ?! or ?? evaluation. This is a way to have fun by picking random move but still from your repertoire!
![image](https://github.com/user-attachments/assets/2d5bbdf4-ebee-4fa3-8d0d-a6da874f8382)
