import sys
import subprocess as sp
import re

from collections import defaultdict

from peo.util import format_message


ParseError = TypeError, AssertionError, IndexError


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

    ops_main = operations['main']
    _, imm = parse_empty_main(ops_main, 0)

    print('int main() {')
    print(f'    return {imm};')
    print('}')


def parse_empty_main(ops, i):
    i, _ = parse_command(ops, i, 'endbr64')
    i, pushargs = parse_command(ops, i, 'push')
    assert pushargs == ['rbp']
    i, movargs = parse_command(ops, i, 'mov')
    assert movargs == ['rbp', 'rsp']
    i, imm = parse_return_imm(ops, i)
    i, _ = multi0(ops, i, lambda ops, i: parse_command(ops, i, 'nop'))
    return i, imm


def multi0(ops, i, parse):
    ret = []
    while True:
        try:
            i, r = parse(ops, i)
            ret.append(r)
        except ParseError:
            break
    return i, ret


def parse_return_imm(ops, i):
    i, imm = parse_mov_eax_imm(ops, i)
    i, popargs = parse_command(ops, i, 'pop')
    assert popargs[0] == 'rbp'
    i, _ = parse_command(ops, i, 'ret')
    return i, imm


def parse_mov_eax_imm(ops, i):
    i, movargs = parse_command(ops, i, 'mov')
    assert movargs[0] == 'eax'
    match = re.match('0x([0-9a-f]+)', movargs[1])
    assert match
    return i, int(match.group(1), 16)


def parse_command(ops, i, name):
    assert i < len(ops)
    assert ops[i].name == name
    return i+1, ops[i].args


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
        args = '' if len(self.args) == 0 else ' ' + ' '.join(self.args)
        return f'{hex(self.addr)}: {self.name}{args}'
