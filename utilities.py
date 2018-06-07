import re

ID = r"([A-Za-z]([A-Za-z]|[0-9])*)"
NUM = r"((\+|-)?([0-9])+)"
keyword1 = r"(EOF|int|void|if|else|while|return)"
keyword2 = r"(;|\[|\]|\(|\)|\{|\}|,|=|<|==|\+|\*|-)"
nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','y']
terminals = ['$',')','(','*','+',',','-',';','<','=','[',']','e','f','g','i','n','q','r','v','w','z','{','}']

contiguousSubString = ""
tokens = []
eofWatch = False
tokenNum = 0
isNum = False

class Node:
    def __init__(self, n, b, s, p):
        self.name = n
        self.base = b
        self.symbolTable = s
        self.parent = p
        self.children = []

    def printSubTree(self, tn):
    	print "{}********************{}*{}".format(tn, self.name, self.base)
    	print self.symbolTable
    	# for k in self.symbolTable.keys():
    		# print tabs + "{}: {}, {}, {}".format(self.symbolTable[k][0], self.symbolTable[k][1], self.symbolTable[k][2])
    	for n in self.children:
    		n.printSubTree(tn + 1)

    def setSymbol(self, ls, ra, lt, ln):
    	self.symbolTable[ls] = [ra, lt, ln]

    def duplicate(self, symbol):
    	return symbol in self.symbolTable


state1 = 0
s1Ind = 0
state2 = 0
lastType = ""
lastSymbol = ""
lastNum = 0
globalAddress = 100
relAddress = 0
currentNode = Node("", globalAddress, {}, None)
root = currentNode

mapping = { "else": "e",
			"if": "f",
			"int": "g",
			"return": "r",
			"void": "v",
			"while": "w",
			"EOF":"z" }	

numSignIndicator = ['[','(','*','=',',','+','-','<','q','e','r']



def matchToken(candid):
	global contiguousSubString
	global tokens
	global lastSymbol
	global lastNum
	global eofWatch
	global tokenNum
	global isNum

	if (contiguousSubString[0] == '+' or contiguousSubString[0] == '-') and candid == "Keyword" :
						if (tokens[-1] in numSignIndicator and tokens[-1] != ')')\
						    or (\
						    tokens[-1] == ')' and (\
						    tokens[len(tokens) - tokens[::-1].index('(') - 2] == 'w' or \
						    tokens[len(tokens) - tokens[::-1].index('(') - 2] == 'f')) :
							isNum = True

	if candid == "Keyword" and not isNum:
		keyword = r"\A" + "(" + keyword2 + "|(" + keyword1 + "(?!" + "[A-Za-z0-9]" + ")))"
		sKey = re.match(keyword, contiguousSubString)
		if sKey :#and ((sKey.group() != "+" and sKey.group() != "-") or checkPrev("n") or checkPrev("i") or checkPrev("y)") or checkPrev("]") or (checkPrev("(P)") and not checkPrev("f(P)") and not checkPrev("w(P)"))) :
			sKey = sKey.group()
			if len(tokens) > 1 and tokens[len(tokens) - 1] == "=" and sKey == "=" :
				tokens[len(tokens) - 1] = "q"
			else :
				if sKey in mapping.keys() :
					tokens.append(mapping[sKey])
					tokenNum = tokenNum + 1
				else :
					tokens.append(sKey)
					tokenNum = tokenNum + 1
			contiguousSubString = re.sub(keyword, "", contiguousSubString)
			if sKey == "EOF" :
				eofWatch = True
				tokens.append('$')
				tokenNum = tokenNum + 1
			return True
		else :
			return False

	if candid == "ID" or candid == "NUM" :
		if candid == "NUM" :
			isNum = False

		pattern = (r"\A" + ID) if candid == "ID" else (r"\A" + NUM)
		matched = re.match(pattern, contiguousSubString)
		if matched :
			matched = matched.group()
			tag = "i" if candid == "ID" else "n"
			tokens.append(tag)
			tokenNum = tokenNum + 1
			if candid == "ID": lastSymbol = matched
			if candid == "NUM": lastNum = int(matched)
			contiguousSubString = re.sub(pattern, "", contiguousSubString)
			return True
		else :
			return False


def getRules(file):
	rules = []
	with open(file, "r") as grammarFile :
		for i in range(55) :
			rule = grammarFile.readline().split("\t")
			rules.append([rule[0], (len(rule[1]) - 1) * 2])

	return rules


def getGotoTable(file):
	with open(file, "r") as gotoTableFile :
		string = gotoTableFile.read()

	gotoTable = {}
	for i in nonTerminals :
		gotoTable[i] = {}

	iterator = 0
	for i in range(0, 96) :
		for j in nonTerminals :
			gotoTable[j][str(i)] = string[(iterator * 4) + i * 113: ((iterator + 1) * 4 + i * 113)].replace(' ', '')
			iterator = iterator + 1
		iterator = 0

	return gotoTable


def getActionTable(file):
	with open(file, "r") as actionTableFile:
		string = actionTableFile.read()

	actionTable = {}
	for i in terminals :
		actionTable [i] = {}

	iterator = 0
	for i in range(0, 96) :
		for j in terminals :
			actionTable[j][str(i)] = string[(iterator * 4) + i * 97: ((iterator + 1) * 4 + i * 97)].replace(' ', '')
			iterator = iterator + 1
		iterator = 0

	return actionTable


def getFollowSet(file):
	followSet = {'A':'','B':'','C':'','D':'','E':'','F':'','G':'','H':'','I':'','J':'','K':'','L':'','M':'','N':'','O':'','P':'','Q':'','R':'','S':'','T':'','U':'','V':'','W':'','X':'','Y':'','Z':'','x':'','y':''}
	keyList = followSet.keys();
	keyList.sort()
	with open(file, "r") as fSetFile :
		for i in keyList :
			followSet[i] = fSetFile.readline().replace('\n','')

	return followSet


def checkPrev(s, SS):
	matches = True
	n = len(s)
	m = len(SS)
	for i in range(n) :
		if SS[m - 1 - i] != s[n - 1 - i] :
			matches = False

	return matches


def semantics(t):
	global s1Ind
	global state1
	global currentNode
	global globalAddress
	global relAddress
	global lastSymbol
	global lastNum

	# print "token = {} and state1 = {}".format(t, state1)

	if state1 == 0:
		state1 = 1 if (t == "g" or t == "v") else (9 if t == "z" else 0)

	elif state1 == 1:
		state1 = 2 if t == "i" else -1

	elif state1 == 2: 
		if t == "(":
			node = Node(lastSymbol, globalAddress, {}, currentNode)
			currentNode.children.append(node)
			currentNode = node
			relAddress = 0
			state1 = 3
		else:
			state1 = 0

	elif state1 == 3:
		state1 = 4 if t == ")" else 3

	elif state1 == 4:
		if t == "{":
			state1 = 5
			s1Ind = 0
		else: state1 = -1

	elif state1 == 5:
		if t == "{":
			node = Node("", globalAddress, {}, currentNode)
			currentNode.children.append(node)
			currentNode = node
			relAddress = 0
			s1Ind = s1Ind + 1
		elif t == "}":
			currentNode = currentNode.parent
			if s1Ind == 0:
				state1 = 0
			else:
				s1Ind = s1Ind - 1
		else:
			state1 = 6 if (t == "f" or t == "w") else (8 if t == "e" else 5)

	elif state1 == 6:
		state1 = 7 if t == "(" else -1

	elif state1 == 7:
		if t == ")":
			state1 = 8

	elif state1 == 8:
		if t == "{":
			node = Node("", globalAddress, {}, currentNode)
			currentNode.children.append(node)
			currentNode = node
			relAddress = 0
			state1 = 5
			s1Ind = s1Ind + 1
		elif t == "f" or t == "w":
			state1 = 6
		elif t != "e":
			state1 = 5

	# print "state1 = {}".format(state1)
	# print "*****"
	return "Syntax Error in Variable Scoping!" if state1 == -1 else addVars(t)


def addVars(t):
	global state2
	global lastType
	global currentNode
	global lastSymbol
	global lastNum
	global globalAddress
	global relAddress

	# print "token = {} and state2 = {}".format(t, state2)

	if state2 == 0:
		if t == "g" or t == "v":
			state2 = 1
			lastType = "int" if t == "g" else "void"
			lastNum = 1

	elif state2 == 1:
		state2 = 2 if t == "i" else 0

	elif state2 == 2:
		if t == "(":
			state2 = 0
		elif t == "[":
			state2 = 3
		elif t == ";" or t == ")" or t == ",":
			if currentNode.duplicate(lastSymbol):
				return "Duplicate Variable Definition: {} already exists in this scope!".format(lastSymbol)
			currentNode.setSymbol(lastSymbol, relAddress, lastType, lastNum)
			size = lastNum * (32 if lastType == "int" else 1)
			globalAddress = globalAddress + size
			relAddress = relAddress + size
			state2 = 0
		else:
			state2 = -1

	elif state2 == 3:
		state2 = 4 if t == "n" else -1

	elif state2 == 4:
		state2 = 2 if t == "]" else -1

	# print "state2 = {}".format(state2)
	# print "*****"
	return "Syntax Error in Variable Definition!" if state2 == -1 else "OK!"




