import re
import subprocess as sp
from typing import List


# 両端の空白を削除、文中の連続した空白を半角空白1個に置き換え
def rm_consecutive_spaces(msg: str) -> str:
    return re.sub(r"\s+", " ", msg).strip()


# objdump -(d, D, S) -M intel ./a.out の出力結果はこれを元に付け加える
def format_message(lines: str) -> List[List[str]]:
    lines = lines.split("\n")  # 出力を行で分ける

    msgs = []  # linesを整理したものが入る
    for line in lines:
        if line == "":  # 何もない行はいらない
            continue
        items = re.split("[#\t]", line)  # 行を基本(アドレス、命令、読みやすい命令(、コメント))に分ける

        msg = []  # items(line)を整理したものが入る
        for item in items:
            msg.append(rm_consecutive_spaces(item))
        msgs.append(msg)
    return msgs


def get_section_as_str(filepath: str, section: str, ndx: int) -> str:
    proc = sp.run(
        ["objdump", "-sj", section, filepath],
        encoding="utf-8",
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    proc = proc.stdout.split("\n")[4:-1]
    proc = [[x[1:5], x[6:41]] for x in proc]
    proc[-1][-1] = rm_consecutive_spaces(proc[-1][-1])

    ssaddr = int(proc[0][0], 16)  # sectionの始まるアドレス
    ndx = ndx - ssaddr
    stab = ""
    for line in proc:
        stab += line[1].replace(" ", "")
    stab = re.split("(..)", stab)[1::2]  # ['de', 'ad', 'be', 'ef']

    retstr = []
    for c in stab[ndx:]:
        if c == "00":
            break
        retstr.append(c)
    retstr = "".join([chr(int(x, 16)) for x in retstr])

    return retstr
