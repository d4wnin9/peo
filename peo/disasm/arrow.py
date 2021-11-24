import re
from typing import List, Tuple


class ArrowManager:
    def __init__(self, n: int):
        self.arrows = [[' '] for i in range(n)]
        self.colors = [[0] for i in range(n)]
        self.depth = 1

    # 次に矢印を張ることのできる深さ・色を得る
    def min_empty_col(self, l: int, r: int) -> Tuple[int, int]:
        usedcolors = set()
        recommended_color = 1
        emp = [True for i in range(self.depth)]
        emp[0] = False
        for i in range(l, r+1):
            for j in range(min(self.depth, len(self.arrows[i]))):
                emp[j] = emp[j] and \
                    (self.arrows[i][j] not in ['\u2502', '\u2514', '\u250c'])
                usedcolors.add(self.colors[i][j])
                while recommended_color in usedcolors:
                    recommended_color += 1
        for i in range(self.depth):
            if emp[i]:
                return (i, recommended_color)
        return (self.depth, recommended_color)

    def add_arrow(self, s: int, e: int, col: int, color: int):
        self.depth = max(self.depth, col+1)

        outarrow = list('<' + '\u2500' * (col-1) + ['\u2514', '\u250c'][s < e])
        outcolor = [color for i in range(1+col)]
        self.arrows[s] = outarrow + self.arrows[s][1+col:]
        self.colors[s] = outcolor + self.colors[s][1+col:]

        inarrow = list('>' + '\u2500' * (col-1) + ['\u2514', '\u250c'][s > e])
        incolor = [color for i in range(1+col)]
        self.arrows[e] = inarrow + self.arrows[e][1+col:]
        self.colors[e] = incolor + self.colors[e][1+col:]

        if s > e:
            s, e = e, s
        for i in range(s+1, e):
            while len(self.arrows[i]) <= col:
                self.arrows[i].append(' ')
                self.colors[i].append(0)
            self.arrows[i][col] = '\u2502'
            self.colors[i][col] = color

    def get_arrows(self) -> List[List[str]]:
        ret = []
        for row in self.arrows:
            adjusted_row = row + [' '] * (self.depth - len(row))
            ret.append(list(reversed(adjusted_row)))
        return ret

    def get_colors(self) -> List[List[int]]:
        ret = []
        for row in self.colors:
            adjusted_row = row + [0] * (self.depth - len(row))
            ret.append(list(reversed(adjusted_row)))
        return ret


def flow_arrow(msgs: str) -> Tuple[List[str], List[List[int]]]:
    retarrows = []
    retcolors = []
    insts = []
    for i in range(len(msgs)):
        if re.match("[0-9a-f]+:", msgs[i][0]):
            insts.append(msgs[i])
        else:
            if insts:
                newarrows, newcolors = __arrowing_in_func(insts)
                retarrows += newarrows
                retcolors += newcolors
                insts = []
            retarrows.append('')
            retcolors.append([])
    if insts:
        newarrows, newcolors = __arrowing_in_func(insts)
        retarrows += newarrows
        retcolors += newcolors

    return (retarrows, retcolors)


def __arrowing_in_func(insts: str) -> Tuple[List[str], List[List[int]]]:
    # 基本的に逆から見ていく  矢印終点に辿り着いたら始点まで戻る形で矢を張る
    # 矢を張る区間内で、他の矢と重ならない最も内側の列に矢を張る

    arrowM = ArrowManager(len(insts))
    # 下から上への矢印を処理
    e2b = dict()
    for i in range(len(insts)-1, -1, -1):
        addr = insts[i][0][:-1]
        if addr in e2b:
            for st in e2b[addr]:
                depth, rcolor = arrowM.min_empty_col(i, st)
                arrowM.add_arrow(st, i, depth, rcolor)
            e2b[addr] = []

        if len(insts[i]) < 3 or len(insts[i][2].split()) == 1:
            continue
        opc, opr, *_ = insts[i][2].split()
        if opc[0] != 'j':
            continue
        if re.match('^[0-9a-f]*$', opr) is None:
            continue
        if int(opr, 16) > int(addr, 16):
            continue
        if opr in e2b:
            e2b[opr].append(i)
        else:
            e2b[opr] = [i]

    # 上から下への矢印を処理
    e2b = dict()
    for i in range(len(insts)):
        addr = insts[i][0][:-1]
        if addr in e2b:
            for st in e2b[addr]:
                depth, rcolor = arrowM.min_empty_col(st, i)
                arrowM.add_arrow(st, i, depth, rcolor)
            e2b[addr] = []

        if len(insts[i]) < 3 or len(insts[i][2].split()) == 1:
            continue
        opc, opr, *_ = insts[i][2].split()
        if opc[0] != 'j':
            continue
        if re.match('^[0-9a-f]*$', opr) is None:
            continue
        if int(opr, 16) < int(addr, 16):
            continue
        if opr in e2b:
            e2b[opr].append(i)
        else:
            e2b[opr] = [i]

    newarrows = [''.join(row) for row in arrowM.get_arrows()]
    newcolors = arrowM.get_colors()
    return (newarrows, newcolors)
