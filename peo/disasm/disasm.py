import sys
import subprocess as sp
from typing import Optional
from pprint import pprint

from peo.util import format_message
from peo.disasm.comment import Comment
from peo.disasm.arrow import flow_arrow
from peo.disasm.setcolor import setcolor, arrow_clr
from peo.disasm.indent import organize, indent, combine


def disasm(filepath: str, fcn: Optional[str]=None):
    proc = sp.run(
        ["objdump", "-d", "-M", "intel", filepath],
        encoding="utf-8",
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )

    # objdumpがエラーを出したらやめるっピ
    if proc.returncode != 0:
        print(proc.stderr)
        sys.exit(1)

    msgs = format_message(proc.stdout)

    # 関数名をしていした場合はそこだけ抜き出す
    if fcn is not None:
        tmp = []
        fcn_flag = False  # その関数内のときTrue
        for msg in msgs:
            if len(msg) == 1:
                if f"<{fcn}>" in msg[0]:
                    fcn_flag = True
                else:
                    fcn_flag = False
            if fcn_flag:
                tmp.append(msg)
        msgs = tmp

    msgs = Comment(filepath, msgs).add()
    msgs = organize(msgs)

    arrows, arrowcolors = flow_arrow(msgs)
    indent(arrows, msgs)
    clr_arrows = arrow_clr(arrows, arrowcolors)
    msgs = setcolor(msgs)
    perf_msgs = combine(clr_arrows, msgs)

    # TODO: 出力を揃える
    for i in range(len(perf_msgs)):
        print("   ".join(msgs[i]))
        if len(msgs[i]) != 1 and i+1 != len(msgs):
            if len(msgs[i+1]) == 1:
                print()