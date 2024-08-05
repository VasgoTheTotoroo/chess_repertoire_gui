# C:\Users\vassia\Desktop\echec\transposition_finder\split_pgn.py "game1.txt"

import sys

file = open(sys.argv[1],  encoding="utf-8")
file_str = file.read().split("[Event \"")

for i, s in enumerate(file_str[1:]):
    idx = s.find("[White")+8
    color_name = "White"
    if s[idx] == "?":
        color_name = "Black"
    file_name = s[s.find("["+color_name)+8:s.find("\"", s.find("["+color_name)+8)]+str(i)+".pgn"
    print(file_name)
    f = open(file_name, "w",  encoding="utf-8")
    f.write(s)
    f.close()
