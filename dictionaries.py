"""The dictionaries used in this project"""

evaluation_dict = {
    "$1": "!",
    "$2": "?",
    "$3": "!!",
    "$4": "??",
    "$5": "!?",
    "$6": "?!",
    "$8": "only_move",
    "$22": "Zugzwang",
    "$16": "W_advantage",
    "$18": "+-",
    "$11": "=",
    "$13": "not_clear",
    "$15": "little_B_advantage",
    "$17": "B_advantage",
    "$19": "-+",
    "$44": "compensation",
    "$40": "attack",
    "$36": "initiative",
    "$132": "counterplay",
    "$138": "zeitnot",
    "$32": "development_advantage",
    "$146": "N",
    "$140": "with_the_idea",
    "$14": "little_W_advantage",
}
reversed_eval_dict = {v: k for k, v in evaluation_dict.items()}

eval_color = {
    "$1": "#5c8bb0",
    "$2": "#e6912c",
    "$3": "#1baca6",
    "$4": "#b33430",
    "$5": "#7979a1",
    "$6": "#f0c15c",
}

file_dict = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
reversed_file_dict = {v: k for k, v in file_dict.items()}

rank_dict = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
reversed_rank_dict = {v: k for k, v in rank_dict.items()}
