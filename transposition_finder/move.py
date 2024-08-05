class Move():
    def __init__(self, name, fen=None, comments=None, parent=None, evaluation=None, main_variant=True):
        self.name = name
        self.parent = parent
        self.fen = fen
        self.comments = comments
        self.evaluation = evaluation
        self.children = []
        self.main_variant = main_variant

    def __str__(self, com_fen=False, full_str = False) -> str:
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
        fen2 = __value.fen[:__value.fen.find(" ", __value.fen.find(" ")+1)]
        # print("1:"+fen1)
        # print("2:"+fen2)
        if fen1 == fen2:
            return True
        return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.fen[:self.fen.find(" ", self.fen.find(" ")+1)])

    def str_to_root(self):
        if self.parent is None:
            return self.name
        string = self.name
        return self.parent.str_to_root()+" "+string