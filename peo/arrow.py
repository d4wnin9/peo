import re


class ArrowManager:
	def __init__(self, n: int):
		self.arrows = [[' '] for i in range(n)]
		self.depth = 1

	def min_empty_col(self, l: int, r: int) -> int:
		emp = [True for i in range(self.depth)]
		emp[0] = False
		for i in range(l, r+1):
			for j in range(min(self.depth, len(self.arrows[i]))):
				emp[j] = emp[j] and (self.arrows[i][j] not in ['\u2502', '\u2514', '\u250c'])
		for i in range(self.depth):
			if emp[i]: return i
		return self.depth
	
	def add_arrow(self, s: int, e: int, col: int):
		self.depth = max(self.depth, col+1)
		outarrow = list('<' + '\u2500' * (col-1) + ['\u2514','\u250c'][s<e])
		inarrow = list('>' + '\u2500' * (col-1) + ['\u2514','\u250c'][s>e])
		self.arrows[s] = outarrow + self. arrows[s][1+col:]
		self.arrows[e] = inarrow + self.arrows[e][1+col:]
		if s > e: s, e = e, s
		for i in range(s+1, e):
			while len(self.arrows[i]) <= col:
				self.arrows[i].append(' ')
			self.arrows[i][col] = '\u2502'
	
	def output(self):
		ret = []
		for row in self.arrows:
			adjusted_row = row + [' '] * (self.depth - len(row))
			ret.append(list(reversed(adjusted_row)))
		return ret


def add_flow_arrow(msgs: str) -> str:
	ret = []
	insts = []
	for i in range(3, len(msgs)):
		if re.match("[0-9a-f]+:", msgs[i][0]):
			insts.append(msgs[i])
		else:
			if insts:
				ret += __arrowing_in_func(insts)
				insts = []
			ret.append(msgs[i])
	if insts:
		ret += __arrowing_in_func(insts)

	return ret


def __arrowing_in_func(insts: str) -> list:
	# 基本的に逆から見ていく  矢印終点に辿り着いたら始点まで戻る形で矢を張る
	# 終点が同じ2つの矢があると上のやつしかできない 要修正

	arrowM = ArrowManager(len(insts))
	e2b = dict()
	# 下から上への矢印を処理
	for i in range(len(insts)-1, -1, -1):
		addr = insts[i][0][:-1]
		if addr in e2b:
			st = e2b[addr]
			depth = arrowM.min_empty_col(i, st)
			arrowM.add_arrow(st, i, depth)
			
		if len(insts[i]) < 3 or len(insts[i][2].split()) == 1: continue
		opc, opr, *_ = insts[i][2].split()
		if opc[0] != 'j': continue
		if re.match('^[0-9a-f]*$', opr) is None: continue
		if int(opr, 16) > int(addr, 16): continue
		e2b[opr] = i
	
	e2b = dict()
	for i in range(len(insts)):
		addr = insts[i][0][:-1]
		if addr in e2b:
			st = e2b[addr]
			depth = arrowM.min_empty_col(st, i)
			arrowM.add_arrow(st, i, depth)
		
		if len(insts[i]) < 3 or len(insts[i][2].split()) == 1: continue
		opc, opr, *_ = insts[i][2].split()
		if opc[0] != 'j': continue
		if re.match('^[0-9a-f]*$', opr) is None: continue
		if int(opr, 16) < int(addr, 16): continue
		e2b[opr] = i

	for i, arrowrow in enumerate(arrowM.output()):
		insts[i] = [''.join(arrowrow)] + insts[i]
	return insts
	
