import sys
import subprocess as sp
import re

from collections import defaultdict

from peo.util import format_message


def decompile(filepath):
    proc = sp.run(
        ["objdump", "-d", "-M", "intel", filepath],
        encoding="utf-8",
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )

    if proc.returncode != 0:
        print(proc.stderr)
        sys.exit(1)

    msgs = format_message(proc.stdout)
    operations = parse_operations(msgs)

    print('int main() {')
    for op in operations['main']:
        if op.name == 'mov' and op.args[0] == 'eax':
            print(f'    int ret = {op.args[1]};')
        elif op.name == 'ret':
            print('    return ret;')
    print('}')


def parse_operations(msgs):
    operations = defaultdict(list)
    current_label = None
    for msg in msgs:
        if re.match('[0-9a-f]{4}:', msg[0]):
            if current_label:
                operations[current_label].append(Op(msg))
        else:
            match = re.match('([0-9a-f]{16}) <([^>]*)>', msg[0])
            if match:
                current_label = match.group(2)
    return operations


class Op:
    def __init__(self, op):
        self.addr = int(op[0][:4], 16)
        if len(op) >= 3:
            op = op[2].split(' ')
            self.name = op[0]
            if len(op) >= 2:
                self.args = op[1].split(',')
            else:
                self.args = []
        else:
            self.name = 'nop'
            self.args = []

    def __repr__(self):
        args = '' if len(self.args) == 0 else ' ' + ','.join(self.args)
        return f'Op({hex(self.addr)}: {self.name}{args})'
