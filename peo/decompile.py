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
    num_of_vars = count_num_of_vars(ops_main)
    _, (ret_val, stmts) = parse_empty_main(ops_main, 0, num_of_vars)

    print('int main() {')
    if num_of_vars > 0:
        print(f'    int {", ".join("x"+str(i) for i in range(num_of_vars))};')
    for stmt in stmts:
        print(f'    {str(stmt)};')
    print(f'    return {ret_val};')
    print('}')


def count_num_of_vars(ops):
    num = 0
    for op in ops:
        for arg in op.args:
            match = re.match(r'DWORD PTR \[rbp-0x([0-9a-f]+)\]', arg)
            if match:
                num = max(num, int(match.group(1), 16)//4)
    return num


def parse_empty_main(ops, i, num_of_vars):
    i, _ = parse_command(ops, i, 'endbr64')
    i, pushargs = parse_command(ops, i, 'push')
    assert pushargs == ['rbp']
    i, movargs = parse_command(ops, i, 'mov')
    assert movargs == ['rbp', 'rsp']
    i, stmts = multi0(ops, i, lambda ops, i: parse_stmt(ops, i, num_of_vars))
    i, imm = parse_return(ops, i, num_of_vars)
    i, _ = multi0(ops, i, lambda ops, i: parse_command(ops, i, 'nop'))
    return i, (imm, stmts)


def parse_stmt(ops, i, num_of_vars):
    def assign(ops, i): return parse_assign(ops, i, num_of_vars)
    def add(ops, i): return parse_add(ops, i, num_of_vars)
    i, stmt = alt(ops, i, assign, add)
    return i, stmt


def parse_assign(ops, i, num_of_vars):
    i, movargs = parse_command(ops, i, 'mov')
    var = parse_var(movargs[0], num_of_vars)
    val = parse_imm_or_var(movargs[1], num_of_vars)
    return i, Assign(var, val)


def parse_add(ops, i, num_of_vars):
    i, addargs = parse_command(ops, i, 'add')
    var = parse_var(addargs[0], num_of_vars)
    val = parse_imm(addargs[1])
    return i, Add(var, val)


def multi0(ops, i, parse):
    ret = []
    while True:
        try:
            i, r = parse(ops, i)
            ret.append(r)
        except ParseError:
            break
    return i, ret


def alt(ops, i, parse0, parse1):
    try:
        i0, ret0 = parse0(ops, i)
    except ParseError:
        i0 = None
    try:
        i1, ret1 = parse1(ops, i)
    except ParseError:
        i1 = None
    assert i0 is not None or i1 is not None
    if i0 is None:
        return i1, ret1
    elif i1 is None:
        return i0, ret0
    elif i0 < i1:
        return i1, ret1
    else:
        return i0, ret0


def parse_return(ops, i, num_of_vars):
    i, ret = parse_mov_eax(ops, i, num_of_vars)
    i, popargs = parse_command(ops, i, 'pop')
    assert popargs[0] == 'rbp'
    i, _ = parse_command(ops, i, 'ret')
    return i, ret


def parse_mov_eax(ops, i, num_of_vars):
    i, movargs = parse_command(ops, i, 'mov')
    assert movargs[0] == 'eax'
    return i, parse_imm_or_var(movargs[1], num_of_vars)


def parse_imm_or_var(arg, num_of_vars):
    try:
        return parse_imm(arg)
    except ParseError:
        return parse_var(arg, num_of_vars)


def parse_imm(arg):
    match = re.match('0x([0-9a-f]+)', arg)
    assert match
    return str(int(match.group(1), 16))


def parse_var(arg, num_of_vars):
    match = re.match(r'DWORD PTR \[rbp-0x([0-9a-f]+)\]', arg)
    assert match
    var = num_of_vars - int(match.group(1), 16)//4
    return f'x{var}'


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
                self.args = ' '.join(op[1:]).split(',')
            else:
                self.args = []
        else:
            self.name = 'nop'
            self.args = []

    def __repr__(self):
        # debug 用
        return f'{hex(self.addr)}: {self.name}({", ".join(self.args)})'


class Stmt:
    def __init__(self):
        pass

    def __str__(self):
        return '// unimplemented stmt'


class Add(Stmt):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def __str__(self):
        return f'{self.var} += {self.val}'


class Assign(Stmt):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def __str__(self):
        return f'{self.var} = {self.val}'
