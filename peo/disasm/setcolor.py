import os
from peo.util import Color


# 命令系統で分類
jumper = [
    "jmp", "ja", "jae", "jb", "jbe", "jc", "jcxz", "je",
    "jg", "jge", "jl", "jle", "jna", "jnae", "jnb", "jnbe",
    "jnc", "jne", "jng", "jnge", "jnl", "jnle", "jno", "jnp",
    "jns", "jnz", "jo", "jp", "jpe", "jpo", "js", "jz"
]

caller = ["call", "lcall"]

stacker = ["push", "pop", "leave"]

calc = ["add", "sub", "and", "or", "xor"]

# 色と関数
clr_func = {
    "normal": Color.normalify, "black": Color.blackify, "red": Color.redify,
    "green": Color.greenify, "yellow": Color.yellowify, "blue": Color.blueify,
    "purple": Color.purplify, "cyan": Color.cyanify, "bold": Color.boldify,
    "highlight": Color.highlightify, "underline": Color.underlinify,
    "blink": Color.blinkify, "bg_black": Color.bg_blackify,
    "bg_red": Color.bg_redify, "bg_green": Color.bg_greenify,
    "bg_yellow": Color.bg_yellowify, "bg_blue": Color.bg_blueify,
    "bg_purple": Color.bg_purplify, "bg_cyan": Color.bg_cyanify,
    "bg_white": Color.bg_whiteify
}

# 配色辞書
asem_color = {
    "jumper": Color.yellowify, "caller": Color.redify,
    "stacker": Color.purplify, "calc": Color.blueify,
    "other": Color.normalify, "func": Color.greenify,
    0: Color.normalify, 1: Color.redify, 2: Color.yellowify,
    3: Color.greenify, 5: Color.blueify, 6: Color.purplify,
    7: Color.cyanify
}


# 必要なアセンブラ部と命令部の取り出し
def setcolor(msgs):
    __make_dict()
    for i in range(len(msgs)):
        if len(msgs[i]) == 4:
            if msgs[i][3][0] == ';':
                msgs[i][3] = Color.greenify(msgs[i][3])
            else:
                msg = msgs[i][2].split(" ")
                msgs[i][2] = __inner_setcolor(msgs[i][2], msg)

        elif len(msgs[i]) == 3:
            msg = msgs[i][2].split(" ")
            msgs[i][2] = __inner_setcolor(msgs[i][2], msg)

        elif len(msgs[i]) == 1:
            if "<" in msgs[i][0]:
                msgs[i][0] = asem_color["func"](msgs[i][0])
                msgs[i+1][0] = asem_color["func"](msgs[i+1][0])

    return msgs


# ユーザー定義の配色に
def __make_dict():
    global asem_color
    try:
        with open(os.path.join(os.environ['HOME'], ".peorc"), 'r') as d:
            set_c = [s.replace("\n", "").split(" ") for s in d.readlines()]

        for i in range(len(set_c)):
            key = set_c[i][0]
            clr = set_c[i][2]
            user_f = clr_func[clr]
            asem_color[key] = user_f
    except FileNotFoundError:
        pass


# 配色と適用
def __inner_setcolor(msgs, msg):
    if msg[0] in jumper:
        c_msgs = asem_color["jumper"](msgs)

    elif msg[0] in caller:
        c_msgs = asem_color["caller"](msgs)

    elif msg[0] in stacker:
        msg[0] = asem_color["stacker"](msg[0])
        c_msgs = ' '.join(msg)

    elif msg[0] in calc:
        msg[0] = asem_color["calc"](msg[0])
        c_msgs = ' '.join(msg)

    else:
        msg[0] = asem_color["other"](msg[0])
        c_msgs = ' '.join(msg)

    return c_msgs


# 矢印に色をつける
def arrow_clr(arrows, clr_nums):
    for i, clr_num in zip(range(len(arrows)), clr_nums):
        if len(arrows[i]) != 0:
            split_arrow = []
            for j in range(len(arrows[i])):
                split_arrow.append(arrows[i][j])

            for s in range(len(split_arrow)):
                key = clr_num[s] % 8
                split_arrow[s] = asem_color[key](split_arrow[s])
            arrows[i] = ''.join(split_arrow)

    return arrows
