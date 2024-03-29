﻿import re

ID = r"([A-Za-z]([A-Za-z]|[0-9])*)"
# DEBUGGED
NUM = r"((\+|-)?([0-9])+(?!([A-Za-z]|[0-9])))"
# DEBUGGED
keyword1 = r"(EOF|int|void|if|else|while|return)"
keyword2 = r"(;|\[|\]|\(|\)|\{|\}|,|=(?!=)|<|==|\+|\*|-)"
nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','t','u','s','w1','y','c','d','h','x2','x4','x7','x5','x6','k','x9','o','m','r1','p','w2','j','b','a','x3','x1','x8','l']
terminals = ['(',')','*','+',',','-',';','<','=','[',']','e','f','g','i','n','q','r','v','w','z','{','}','$']
badString = ""

contiguousSubString = ""
tokens = []
eofWatch = False
tokenNum = 0
isNum = False
tokenSemaphore = 0
globalAddress = 0

doubleLastFunc = ''

LOCALBASE = 500
TEMPBASE = 1000
ARRAYBASE = 1500
# secondLastSymbol = ''
# class Node:
# 	def __init__(self, p):
# 		self.returned = False
# 		self.children = []
# 		self.parent = None

# 	def checkReturned(self):
# 		if self.returned:
# 			print "returned"
# 			return
# 		else:
# 			for c in self.children:
# 				r = True
# 				if cc in c:
# 					if not cc.checkReturned():
# 						r = False
# 				if r:
# 					self.returned = True
# 					print "returned"
# 					return
# 			print "not returned"
# 			return


class BlockNode:
    def __init__(self, fun, n, s, p):
    	self.function = fun
        self.name = n
        self.symbolTable = s
        self.parent = p
        self.children = []
        # self.root = Node(p.curNode if p else None)
        # self.curNode = self.root

    def printSubTree(self, tn):
    	print "{} ******************** {}".format(tn, self.name)
    	print self.symbolTable
    	for n in self.children:
    		n.printSubTree(tn + 1)

    def setSymbol(self, ls, ra, raa, ln, ia):
    	self.symbolTable[ls] = [ra, raa, ln, ia]

    def duplicate(self, symbol):
    	return symbol in self.symbolTable


# arrayAddressBase = 1000
# arrayAddressCounter = 0
# localAddressBase = 100
# localAddressCounter = 0
# tempAddressBase = 500
# tempAddressCounter = 0

state1 = 0
scopeCounter = 0
state2 = 0
state3 = 0
lastType = ""
lastSymbol = ""
lastNum = 1
isArray = False
relAddress = LOCALBASE
relArrAddress = ARRAYBASE
tempAddress = TEMPBASE
currentBlockNode = BlockNode(True, "", {}, None)
functions = {'output':['void', -1, {'x': [-4, -1, 1, False]}]}

semanticStack = []
programBlock = []
programBlock.append(['ASSIGN','#5000',1000000,'']) # Stack pointer! 
programBlock.append(['ASSIGN','#5000',2000000,'']) # Inside of stack pointer! 
programBlock.append(['ASSIGN','#0',3000000,'']) # Return value
programBlock.append(['ASSIGN','#10000000',4000000,'']) # Control link
programBlock.append(['ASSIGN','#0',5000000,'']) # Access link
programBlock.append(['ASSIGN','#0',10000000,''])
programBlockPointer = 6
tokenIterator = 0
lastFunc = ''
isFirstFunc = False

baseStackPointer = 1000000
stackPointer = 2000000
returnAddress = 3000000
controlLink = 4000000
accessLink = 5000000

mapping = { "else": "e",
			"if": "f",
			"int": "g",
			"return": "r",
			"void": "v",
			"while": "w",
			"EOF": "z",
			"==": "q"}	

numSignIndicator = ['[','(','*','=',',','+','-','<','q','e','r']


def getTemp():
	global tempAddress

	a = tempAddress
	tempAddress = tempAddress + 4
	return a


def matchToken(candid):
	global contiguousSubString
	global tokens
	global lastSymbol
	global lastNum
	global eofWatch
	global tokenNum
	global isNum
	global lastFunc
	global tokenSemaphore
	global badString

	if (contiguousSubString[0] == '+' or contiguousSubString[0] == '-') and candid == "Keyword" :
		if (tokens[-1][0] in numSignIndicator and tokens[-1][0] != ')') :
			isNum = True
		elif tokens[-1][0] == ')' and (\
		    	tokens[len(tokens) - tokens[::-1].index(('(','(')) - 2][0] == 'w' or \
		    	tokens[len(tokens) - tokens[::-1].index(('(','(')) - 2][0] == 'f') :
				isNum = True

	if candid == "Keyword" and not isNum:
		keyword = r"\A" + "(" + keyword2 + "|(" + keyword1 + "(?!" + "[A-Za-z0-9]" + ")))"
		sKey = re.match(keyword, contiguousSubString)
		if sKey :
			sKey = sKey.group()
			# if len(tokens) > 1 and tokens[len(tokens) - 1][0] == "=" and sKey == "=" :
			# 	tokens[len(tokens) - 1] = ('q','==')
			# else :
			# print sKey
			if sKey in mapping.keys() :
				tokens.append((mapping[sKey], sKey))
				tokenNum = tokenNum + 1
				tokenSemaphore = 1
			else :
				tokens.append((sKey, sKey))
				tokenNum = tokenNum + 1
				tokenSemaphore = 1
			contiguousSubString = re.sub(keyword, "", contiguousSubString)
			if sKey == "EOF" :
				eofWatch = True
				tokens.append(('$', 'none'))
				tokenNum = tokenNum + 1
				tokenSemaphore = 1
			return True
		else :
			badString = contiguousSubString
			return False

	if candid == "ID" or candid == "NUM" :
		if candid == "NUM" :
			isNum = False

		pattern = (r"\A" + ID) if candid == "ID" else (r"\A" + NUM)
		matched = re.match(pattern, contiguousSubString)
		if matched :
			matched = matched.group()
			# print matched + " --> " + candid
			tag = "i" if candid == "ID" else "n"
			tokens.append((tag, matched))
			tokenNum = tokenNum + 1
			tokenSemaphore = 1
			contiguousSubString = re.sub(pattern, "", contiguousSubString)
			return True
		else :
			badString = contiguousSubString
			return False


def getRules(file):
	rules = []
	with open(file, "r") as grammarFile :
		for i in range(81) :
			rule = grammarFile.readline().split("\t")
			if not i in [32, 34, 35, 40, 42, 43, 44, 49, 6, 50, 9] :
				rules.append([rule[0], (len(rule[1]) - 1) * 2])
			elif i != 50 :
				rules.append([rule[0], ((len(rule[1]) - 1) - 1) * 2])
			elif i == 50 :
				rules.append([rule[0], 14])
			else :
				rules.append([rule[0], 16])
	# print rules

	return rules


def getGotoTable(file):
	with open(file, "r") as gotoTableFile :
		string = gotoTableFile.read()

	gotoTable = {}
	for i in nonTerminals :
		gotoTable[i] = {}

	iterator = 0
	for i in range(0, 122) :
		for j in nonTerminals :
			gotoTable[j][str(i)] = string[(iterator * 4) + i * 217: ((iterator + 1) * 4 + i * 217)].replace(' ', '')
			iterator = iterator + 1
		iterator = 0
	# print gotoTable['x1']['54']

	return gotoTable


def getActionTable(file):
	with open(file, "r") as actionTableFile:
		string = actionTableFile.read()

	actionTable = {}
	for i in terminals :
		actionTable [i] = {}

	iterator = 0
	for i in range(0, 122) :
		for j in terminals :
			actionTable[j][str(i)] = string[(iterator * 4) + i * 97: ((iterator + 1) * 4 + i * 97)].replace(' ', '')
			iterator = iterator + 1
		iterator = 0

	return actionTable


def getFollowSet(file):
  followSet = {}
  #DEBUGGED
  f = {"A": "$", "B": "vgz", "C": "rvfgw(iz{;}n", "D": "rfvwg(i{;}n", "E": "i", "F": "vgz", "G": "vgz", "H": "efg(inrvwz{;}", "I": "),", "J": "rfw(i{;}n", "K": "refw(i{;}n", "L": "refw(i{;}n", "M": "refw(i{;}n", "N": ");,]", "O": "q);+<,-]", "P": ");,]", "Q": "refw(i{;}n", "R": "refw(i{;}n", "S": "q)*;+<,-]", "T": ")", "U": "),", "V": "q)*;+<,=-]", "W": "(in", "X": "q)*;+<,-]", "Y": "(in", "Z": "q)*;+<,-]", "À": "),", "Â": "(in", "Ã": "(in", "Å": ");,]", "Æ": "(in", "È": ")", "É": "refw(i{;}n", "Ê": "e", "Ë": ")", "Ì": "(in", "Í": "q)*;+<,-]", "Î": "q)*;+<,-]", "Ï": "q)*;+<,-]", "Õ": ")", "Ö": "refw(i{;}n", "Ø": "(i)n", "Ù": ")", "Ú": "refw(i{;}n", "Û": "q)*[;+<,=-]", "Ü": "]", "Ā": ");,]", "Ē": "(in", "Ė": "refw(i{;}n", "Ę": "vg", "Ī": "rvfgw(iz{;}n", "Į": "q);+<,-]", "Œ": "vgz", "Ū": "refw(i{;}n"}
  m = {"a"  : "Ę", "b"  : "Ė", "c"  : "É", "d"  : "Ê", "h"  : "Ë", "j"  : "Ē", "k"  : "Ö", "l"  : "Ū", "m"  : "Ú", "o"  : "Ù", "p"  : "Ü", "r1" : "Û", "s"  : "Å", "t"  : "Â", "u"  : "Ã", "w1" : "Æ", "w2" : "Ā", "x1" : "Į", "x2" : "Ì", "x3" : "Ī", "x4" : "Í", "x5" : "Ï", "x6" : "Õ", "x7" : "Î", "x9" : "Ø", "x8" : "Œ", "x"  : "À", "y"  : "È"}
  #DEBUGGED
  for k in sorted(f.keys()):
    m[k] = k
    if k == "Z":
      break
  for mm in sorted(m.keys()):
    followSet[mm] = f[m[mm]]
    # print mm + "\t" + f[m[mm]]

  return followSet


def semantics(token):
	t = token[0]

	if t == "z" and not ("main" in functions.keys()):
		return "The \'main\' function has not been defined!"

	stat = scopeChecking(t)
	if stat == "OK!":
		stat = addVars(t)
		if stat == "OK!":
			stat = funTypeChecking(t)
			return stat
		else: return stat
	else: return stat


def scopeChecking(t):
	global scopeCounter
	global state1
	global currentBlockNode
	global relAddress
	global relArrAddress
	global tempAddress
	global lastSymbol
	global lastNum
	global lastFunc
	global doubleLastFunc

	if state1 == 0:
		state1 = 1 if (t == "g" or t == "v") else (9 if t == "z" else 0)

	elif state1 == 1:
		state1 = 2 if t == "i" else -1

	elif state1 == 2: 
		if t == "(":
			# Checking whether main is the last function declaration or not!
			if "main" in functions.keys() and lastSymbol != "main":
				return "\'{}\' Is Defined After \'main\'".format(lastSymbol)
			# Checking whether the function defined has a duplicate name as another function or not!
			if lastSymbol in functions.keys():
				return "Duplicate Function Definition: \'{}\' Already Exists!".format(lastSymbol)
			else:
				functions[lastSymbol] = [lastType, -1]
			# Inserting the new identifier inside of the symbol table linked-list
			doubleLastFunc = lastFunc
			lastFunc = lastSymbol
			node = BlockNode(True, lastSymbol, {}, currentBlockNode)
			currentBlockNode.children.append(node)
			currentBlockNode = node
			# currentBlockNode.root.returned = False if lastType == "int" else True
			relAddress = LOCALBASE
			relArrAddress = ARRAYBASE
			tempAddress = TEMPBASE
			state1 = 3
		else:
			state1 = 0

	elif state1 == 3:
		state1 = 4 if t == ")" else 3

	elif state1 == 4:
		if t == "{":
			state1 = 5
			scopeCounter = 0
		else: state1 = -1

	elif state1 == 5:
		if t == "{":
			# Inserting the new scope inside of the symbol table linked-list
			node = BlockNode(False, currentBlockNode.name, {}, currentBlockNode)
			currentBlockNode.children.append(node)
			currentBlockNode.curNode.children.append(node.root)
			currentBlockNode = node
			scopeCounter = scopeCounter + 1
		elif t == "}":
			# currentBlockNode.root.checkReturned()
			if scopeCounter == 0:
				# if not currentBlockNode.root.returned:
				# 	return "Function \'{}\' Has Not Retured A Value".format(currentBlockNode.name)
				state1 = 0
			else:
				scopeCounter = scopeCounter - 1
			currentBlockNode = currentBlockNode.parent
		elif t == "w" or t == "f":
			state1 = 6
			# node = Node(currentBlockNode.curNode)
			# currentBlockNode.curNode.children.append([node])
			# currentBlockNode.curNode = node
		elif t == "e":
			state1 = 8
			# node = Node(currentBlockNode.curNode)
			# currentBlockNode.curNode.children[-1].append(node)
			# currentBlockNode.curNode = node
		# elif t == "r":
		# 	currentBlockNode.root.returned = True
		# 	currentBlockNode.curNode = currentBlockNode.curNode.parent

	elif state1 == 6:
		state1 = 7 if t == "(" else -1

	elif state1 == 7:
		if t == ")":
			state1 = 8

	elif state1 == 8:
		if t == "{":
			node = BlockNode(False, currentBlockNode.name, {}, currentBlockNode)
			currentBlockNode.children.append(node)
			# currentBlockNode.curNode = node.root
			currentBlockNode = node
			state1 = 5
			scopeCounter = scopeCounter + 1
		elif t == "f" or t == "w":
			state1 = 6
			# node = Node(currentBlockNode.curNode)
			# currentBlockNode.curNode.children.append([node])
			# currentBlockNode.curNode = node
		# elif t == "e":
			# node = Node(currentBlockNode.curNode)
			# currentBlockNode.curNode.children[-1].append(node)
			# currentBlockNode.curNode = node
		elif t != "e":
			state1 = 5
			# if t == "r":
			# 	currentBlockNode.curNode.returned = True
			# 	currentBlockNode.curNode = currentBlockNode.curNode.parent

	return "" if state1 == -1 else "OK!"


def addVars(t):
	global state2
	global lastType
	global currentBlockNode
	global lastSymbol
	global lastNum
	global isArray
	global relAddress
	global relArrAddress
	global globalAddress

	if state2 == 0:
		if t == "g" or t == "v":
			state2 = 1
			lastType = "int" if t == "g" else "void"
			isArray = False

	elif state2 == 1:
		state2 = 2 if t == "i" else 0

	elif state2 == 2:
		if t == "(":
			state2 = 0
		elif t == "[":
			state2 = 3
			isArray = True
		elif t == ";" or t == ")" or t == ",":
			if currentBlockNode.duplicate(lastSymbol):
				return "Duplicate Variable Definition: \'{}\' Already Exists In This Scope!".format(lastSymbol)
			if lastType == "void":
				return "Variable \'{}\' Can Not Be Defined Of Type \'void\'".format(lastSymbol)

			aa = -1
			if isArray and not (state1 == 3 or state1 == 4):
				if lastNum < 1:
					return "Can Not Define Array Of Size {}!".format(lastNum)
				else:
					aa = relArrAddress
					relArrAddress = relArrAddress + 4 * lastNum
			currentBlockNode.setSymbol(lastSymbol, relAddress if (currentBlockNode.name != '') else globalAddress, aa, lastNum if isArray else 1, isArray)
			if currentBlockNode.name == '' :
				globalAddress = globalAddress + 4
			else :	
				relAddress = relAddress + 4

			# print relAddress
			state2 = 0
			if t == ")":
				# print "heyyyyyyyyy!"
				functions[currentBlockNode.name].append(currentBlockNode.symbolTable.copy())
				# print functions[currentBlockNode.name]
		else:
			state2 = -1

	elif state2 == 3:
		if t == "n":
			state2 = 4
		elif t == "]":
			state2 = 2
			lastNum = -1
		else:
			state2 = -1

	elif state2 == 4:
		state2 = 2 if t == "]" else -1

	return "" if state2 == -1 else "OK!"


def funTypeChecking(t):
	global state3

	if state3 == 0:
		if t == "r":
			state3 = 1

	elif state3 == 1:
		if t == ";":
			if functions[currentBlockNode.name][0] == "int":
				return "Function \'{}\' Must Return A Value of Type \'int\'".format(currentBlockNode.name)
			state3 = 0;
		else:
			state3 = 2;

	elif state3 == 2:
		if t == ";":
			if functions[currentBlockNode.name][0] == "void":
				return "Function \'{}\' Must Return A Value of Type \'void\'".format(currentBlockNode.name)
		state3 = 0	

	return "OK!"


def findVar(symbol, node):
  n = node
  while n != None:
    if symbol in n.symbolTable.keys() :
      return [n.name, n.symbolTable[symbol]]
    else : n = n.parent

  return None


def addCode(code):
	global programBlock
	global programBlockPointer

	programBlock.append(code)
	programBlockPointer = programBlockPointer + 1


def copyCode1(begin, end):
	global stackPointer
	iterator = begin		
	while iterator < end :
		addCode(['ASSIGN',iterator,'@' + str(stackPointer),''])
		addCode(['ADD',stackPointer,'#4',stackPointer])
		iterator = iterator + 4


def copyCode2(begin, end):
	global stackPointer
	iterator = begin
	while iterator < end  :
		addCode(['ASSIGN','@' + str(stackPointer),iterator,''])
		addCode(['ADD',stackPointer,'#4',stackPointer])
		iterator = iterator + 4


def codeGen(nonTerminal, token):
	global programBlockPointer
	global programBlock
	global semanticStack
	global isFirstFunc
	global lastFunc
	global baseStackPointer
	global stackPointer 
	global returnAddress  
	global controlLink 
	global accessLink 
	global doubleLastFunc
	# global secondLastSymbol

	# print str(semanticStack) + str(nonTerminal) 
	# print programBlock
	# print semanticStack


	if nonTerminal == 'a' :
		# print "we are at " + nonTerminal
		# print str(isFirstFunc) + str(token[1])
		if (not isFirstFunc) : 
			addCode('')
			semanticStack.append(programBlockPointer - 1)
			isFirstFunc = True
		elif token[1] == 'main' :
			pointer = semanticStack.pop()
			# print pointer
			programBlock[pointer] = ['JP',programBlockPointer,'','']

			copyCode1(LOCALBASE, relAddress)

			addCode(['ASSIGN',baseStackPointer,stackPointer,''])
			addCode(['ADD',stackPointer,'#' + str(ARRAYBASE),stackPointer])
			# addCode(['ADD',stackPointer,'#12',stackPointer])
			
			copyCode1(ARRAYBASE, relArrAddress)

			addCode(['ASSIGN',baseStackPointer,stackPointer,''])
			addCode(['ADD',stackPointer,'#' + str(TEMPBASE),stackPointer])
			# addCode(['ADD',stackPointer,'#12',stackPointer])

			copyCode1(TEMPBASE, tempAddress - 4)

			addCode(['ASSIGN',baseStackPointer,stackPointer,''])
			addCode(['ADD',stackPointer,'#' + str(1500),stackPointer])
			addCode(['ADD',baseStackPointer,'#' + str(1500),baseStackPointer])

		functions[token[1]][1] = programBlockPointer
		# print functions[token[1]]
	
	elif nonTerminal == 'b' :
		# print "we are at " + nonTerminal
		# print semanticStack
		# print programBlock
		semanticStack.pop()
	
	elif nonTerminal == 'h' :
		# print "we are at " + nonTerminal
		semanticStack.append(programBlockPointer)
		# print "The semantic stack is at: " + str(semanticStack)
		addCode('')
	
	elif nonTerminal == 'd' :
		# print "we are at " + nonTerminal

		programBlock[semanticStack[-1]] = ['JPF',semanticStack[-2],programBlockPointer + 1,'']
		semanticStack.pop()
		semanticStack.pop()
		semanticStack.append(programBlockPointer)
		addCode('')
	
	elif nonTerminal == 'c' :
		# print "we are at " + nonTerminal
		# print semanticStack[-1]
		# print programBlock[semanticStack[-1]]
		programBlock[semanticStack[-1]] = ['JP',programBlockPointer,'','']
		semanticStack.pop()
	# while
	elif nonTerminal == 'j' :
		# print "we are at " + nonTerminal
		semanticStack.append(programBlockPointer)
	
	elif nonTerminal == 'o' :
		# print "we are at " + nonTerminal
		semanticStack.append(programBlockPointer)
		addCode('')
	
	elif nonTerminal == 'l' :
		# print "we are at " + nonTerminal
		programBlock[semanticStack[-1]] = ['JPF',semanticStack[-2],programBlockPointer + 1,'']
		# print programBlock[semanticStack[-1]]
		addCode(['JP',semanticStack[-3],'',''])
		semanticStack.pop()
		semanticStack.pop()
		semanticStack.pop()
	
	elif nonTerminal == 'k' :
		# print "we are at " + nonTerminal
		
		t = getTemp()

		programBlock.append(['SUB',baseStackPointer,'#1512',baseStackPointer])
		programBlockPointer = programBlockPointer + 1

		programBlock.append(['ASSIGN',str(baseStackPointer),t,''])
		programBlockPointer = programBlockPointer + 1

		programBlock.append(['JP','@' + str(t),'',''])
		programBlockPointer = programBlockPointer + 1

	elif nonTerminal == 'm' :
		# print "we are at " + nonTerminal
		# Return address of the function is pushed at the begining, so just assigning the return value to the return address!
		addCode(['ASSIGN',semanticStack[-1],str(returnAddress),''])
		# t = getTemp()
		# addCode(['ASSIGN',str(controlLink),'@' + str(stackPointer),''])
		# addCode(['ADD',stackPointer,'#4',stackPointer])
		# programBlock.append(['ADD',stackPointer,'#4',stackPointer])
		# # programBlock.append(['ASSIGN',temporary,500,''])
		# programBlockPointer = programBlockPointer + 1
		# semanticStack.append(returnAddress)
		# semanticStack.append(returnAddress)
		# semanticStack.pop()
		

		semanticStack.pop()

		# addCode(['PRINT',str(controlLink),'',''])

		programBlock.append(['JP','@' + str(controlLink),'',''])
		programBlockPointer = programBlockPointer + 1
	
	elif nonTerminal == 'w2' :
		# print "we are at " + nonTerminal
		# print semanticStack
		addCode(['ASSIGN',semanticStack[-1],semanticStack[-2],''])
		semanticStack.pop()
		result = semanticStack.pop()
		semanticStack.append(result)
	
	elif nonTerminal == 'r1' :
		# print "we are at " + nonTerminal
		# temp = getTemp()
		# temp1 = getTemp()
		fv = findVar(token[1], currentBlockNode)
		if fv is None:
			print "Variable \'{}\' Not Found!".format(token[1])
			quit()
		i = fv[1][0]
		# semanticStack.append(programBlockPointer)
		# programBlock.append(['ASSIGN',str(i),temp,''])
		# programBlock.append(['ADD',temp,500,temp1])
		# programBlockPointer = programBlockPointer + 2
		semanticStack.append(str(i))
		# print semanticStack
	
	elif nonTerminal == 'p' :
		# print "we are at " + nonTerminal
		tempAddr1 = getTemp()
		# tempAddr2 = getTemp()
		# gett2 = getTemp()
		# pointer = semanticStack[-3]
		temp = semanticStack.pop()
		address = semanticStack.pop()


		# if currentBlockNode.name != 'main' :
		# 	# print str(functions[currentBlockNode.name][2].keys()) + "Hoooooooyyyy"
		# 	# print currentBlockNode.name

		# 	if len(functions[currentBlockNode.name]) > 2:
		# 		for i in functions[currentBlockNode.name][2].keys() :
		# 			if  address == str(functions[currentBlockNode.name][2][i][0]):
		# 				# print "MAAAAAAAAAAAAAANN"
		# 				addCode(['ADD',accessLink,address,tempAddr1])
		# 				addCode(['ADD',str(temp),tempAddr1,tempAddr1])
		# 				semanticStack.append('@' + str(tempAddr1))

		# 	# elif (currentBlockNode.name == ''):
		# 	# 	addCode(['ADD','#5012',address,tempAddr1])
		# 	# 	addCode(['ADD',str(temp),tempAddr1,tempAddr1])
		# 	# 	# programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		# 	# 	semanticStack.append('@' + str(tempAddr1))
		# 	else :
		# 		# wrongAddresses = programBlock[pointer]
		# 		# wrongAddresses[1] = wrongAddresses[1].replace('#','')
		# 		addCode(['ADD',str(temp),address,tempAddr1])
		# 		# programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		# 		semanticStack.append('@' + str(tempAddr1))
		# 		# print semanticStack
		#  # print str(functions[currentBlockNode.name][2].keys()) + "Hoooooooyyyy"
		#  # print currentBlockNode.name

		#  if len(functions[currentBlockNode.name]) > 2:
		#   for i in functions[currentBlockNode.name][2].keys() :
		#    if  address == str(functions[currentBlockNode.name][2][i][0]):
		#     # print "MAAAAAAAAAAAAAANN"
		#     addCode(['ADD',accessLink,address,tempAddr1])
		#     addCode(['ADD',str(temp),tempAddr1,tempAddr1])
		#     semanticStack.append('@' + str(tempAddr1))

		#  # elif (currentBlockNode.name == ''):
		#  #  addCode(['ADD','#5008',address,tempAddr1])
		#  #  addCode(['ADD',str(temp),tempAddr1,tempAddr1])
		#  #  # programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		#  #  semanticStack.append('@' + str(tempAddr1))
		#  else :
		#   # wrongAddresses = programBlock[pointer]
		#   # wrongAddresses[1] = wrongAddresses[1].replace('#','')
		#   addCode(['ADD',str(temp),address,tempAddr1])
		#   # programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		#   semanticStack.append('@' + str(tempAddr1))
		#   # print semanticStack

		# else :
		# wrongAddresses = programBlock[pointer]
		# wrongAddresses[1] = wrongAddresses[1].replace('#','')
		addCode(['ADD',str(temp),address,tempAddr1])
		# programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		semanticStack.append('@' + str(tempAddr1))
		# print semanticStack

	
	elif nonTerminal == 's' :
		# print "we are at " + nonTerminal
		temp = getTemp()
		firstOperand = semanticStack.pop()
		operation = semanticStack.pop()
		secondOperand = semanticStack.pop()
		addCode(['EQ',firstOperand,secondOperand,temp] if (operation == 'equal') else (['LT',secondOperand,firstOperand,temp] if operation == 'less' else '')) # TODO:Addressing!!!!!!!!
		semanticStack.append(temp)
	
	elif nonTerminal == 't' :
		# print "we are at " + nonTerminal
		semanticStack.append('less')
	
	elif nonTerminal == 'u' :
		# print "we are at " + nonTerminal
		semanticStack.append('equal')
	
	elif nonTerminal == 'x1' :
		# print "we are at " + nonTerminal
		temp = getTemp()
		firstOperand = semanticStack.pop()
		operation = semanticStack.pop()
		secondOperand = semanticStack.pop()
		addCode(['ADD',firstOperand,secondOperand,temp] if operation == 'add' else (['SUB',secondOperand,firstOperand,temp] if operation == 'sub' else '')) # TODO:Addressing!!!!!!!!
		semanticStack.append(temp)
	
	elif nonTerminal == 'w1' :
		# print "we are at " + nonTerminal
		semanticStack.append('add')
	
	elif nonTerminal == 'x2' :
		# print "we are at " + nonTerminal
		semanticStack.append('sub')
	
	# elif nonTerminal == 'x5' :
	
	elif nonTerminal == 'x6' :
		# print "we are at " + nonTerminal
		# temporary = getTemp()
		argsList = []		

		while not semanticStack[-1] == '(' :
			argsList.append(semanticStack.pop())
		semanticStack.pop()
		
		if semanticStack[-1] == 'output' :
			addCode(['PRINT',argsList[0],'',''])
			return 0
		else :
			funcID = semanticStack[-1]
			if (not funcID in functions.keys()) :
				print "Function " + funcID + " not defined" 

			# print argsList
			# print "***"
			# print functions[funcID]

			# DEBUGGED
			l1 = len(argsList)
			l2 = 0 if len(functions[funcID]) == 2 else len(functions[funcID][2])
			if l1 != l2:
				print "Too " + ("Many" if l1 > l2 else "Few") + " Arguments To Call Function \'{}\':".format(funcID) + str(argsList) #TODO: Check parameter types
				quit()
			# DEBUGGED

		# programBlock.append(['PRINT',baseStackPointer,'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',stackPointer,'',''])
		# programBlockPointer = programBlockPointer + 1

		addCode(['ASSIGN',str(returnAddress),'@' + str(stackPointer),''])
		addCode(['ADD',stackPointer,'#4',stackPointer])

		# programBlock.append(['PRINT',str(returnAddress),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# addCode(['ASSIGN',str(controlLink),'@' + str(stackPointer),''])
		addCode(['ASSIGN',str(controlLink),'@' + str(stackPointer),''])
		addCode(['ADD',stackPointer,'#4',stackPointer])

		# programBlock.append(['PRINT',str(returnAddress),'',''])
		# programBlockPointer =  programBlockPointer + 1

		addCode(['ASSIGN',str(accessLink),'@' + str(stackPointer),''])
		addCode(['ADD',stackPointer,'#4',stackPointer])

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		copyCode1(LOCALBASE, relAddress)

		addCode(['ASSIGN',baseStackPointer,stackPointer,''])
		addCode(['ADD',stackPointer,'#' + str(ARRAYBASE),stackPointer])
		addCode(['ADD',stackPointer,'#12',stackPointer])

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		copyCode1(ARRAYBASE, relArrAddress)

		addCode(['ASSIGN',baseStackPointer,stackPointer,''])
		addCode(['ADD',stackPointer,'#' + str(TEMPBASE),stackPointer])
		addCode(['ADD',stackPointer,'#12',stackPointer])

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		copyCode1(TEMPBASE, tempAddress - 4)

		localAddress = LOCALBASE
		# temporaryAddress = TEMPBASE
		# arrAddress = ARRAYBASE

		for iterator in range(len(argsList)) :
			addCode(['ASSIGN',argsList[len(argsList) - iterator - 1],localAddress,''])
			localAddress = localAddress + 4

		# programBlock.append(['ASSIGN',"#0", stackPointer,''])
		# programBlockPointer = programBlockPointer + 1

		addCode(['ASSIGN',baseStackPointer,stackPointer,''])
		addCode(['ADD',stackPointer,'#' + str(1512),stackPointer])

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		addCode(['ASSIGN','@' + str(baseStackPointer), str(accessLink),''])
		addCode(['ADD',baseStackPointer,'#' + str(1512),baseStackPointer])

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# addCode(['ASSIGN','#' + str(programBlockPointer + 1), str(controlLink),''])

		programBlock.append(['ASSIGN','#' + str(programBlockPointer + 2), str(controlLink),''])
		programBlockPointer =  programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		jumpAddress = functions[funcID][1]
		programBlock.append(['JP',jumpAddress,'',''])
		programBlockPointer =  programBlockPointer + 1
	
	elif nonTerminal == 'x7' :
		# print "we are at " + nonTerminal
		temp = getTemp()
		firstOperand = semanticStack.pop()
		secondOperand = semanticStack.pop()
		addCode(['MULT',firstOperand,secondOperand,temp]) # TODO:Addressing!!!!!!!!
		semanticStack.append(temp)
	
	elif nonTerminal == 'x8' :
		# print "we are at " + nonTerminal
		t = getTemp()
		# if lastFunc != 'main':
		# 	print functions[lastFunc]

		# for iterator in xrange(currentBlockNode.children)
		# 	if iterator.name == lastFunc :


		# relativeAddress = 0
		# temporaryAddress = 0
		# arrayAddress = 0
		# temporary = getTemp()
		# # print lastFunc
		# if (not lastFunc == 'main') :
		# 	programBlock.append(['SUB',500,'#4',temporary])
		# 	programBlockPointer = programBlockPointer + 1
			
		# 	programBlock.append(['ASSIGN',199,500,''])
		# 	programBlockPointer = programBlockPointer + 1

		# 	programBlock.append(['JP',92,'',''])
		# 	programBlockPointer = programBlockPointer + 1

		addCode(['SUB',baseStackPointer,'#1512',baseStackPointer])

		addCode(['ASSIGN',str(baseStackPointer),t,''])

		# programBlock.append(['PRINT',t,'',''])
		# programBlockPointer = programBlockPointer + 1

		addCode(['JP','@' + str(t),'',''])

	elif nonTerminal == 'x9' :
		# print "we are at " + nonTerminal
		semanticStack.append(token[1])
		semanticStack.append('(')

	elif nonTerminal == 'C' :
		# print "we are at " + nonTerminal
		# print secondLastSymbol
		# print token
		if token[0] == 'i' :
			tj = tokenIterator - 1
			while tj >= 0:
				if tokens[tj][0] == "i":
					secondLastSymbol = tokens[tj][1]
					break
				tj = tj - 1
			if tj < 0:
				secondLastSymbol = lastSymbol

			fv = findVar(secondLastSymbol, currentBlockNode)
			if fv is None:
				print "Variable \'{}\' Not Found!".format(secondLastSymbol)
				quit()
			i = fv[1][0]
			if not fv[1][-1] == True:
				# print fv[1][-1]
				addCode(['ASSIGN','#0',i,''])
			else :
				fv = findVar(secondLastSymbol, currentBlockNode)
				if fv is None:
					print "Variable \'{}\' Not Found!".format(secondLastSymbol)
					quit()
				i = fv[1][0]
				num = fv[1][-2]
				t = getTemp()
				for index in range(num) :
					addCode(['ADD','#' + str(index * 4),str(i),t])
					addCode(['ASSIGN','#0','@' + str(t),''])
		else :
			fv = findVar(lastSymbol, currentBlockNode)
			if fv is None:
				print "Variable \'{}\' Not Found!".format(lastSymbol)
				quit()
			i = fv[1][0]
			if not fv[1][-1] == True:
				# print fv[1][-1]
				addCode(['ASSIGN','#0',i,''])
			else :
				return 0

	elif nonTerminal == 'x3' :
		# print "we are at " + nonTerminal
		fv = findVar(token[1], currentBlockNode)
		if fv is None:
			print "Variable \'{}\' Not Found!".format(token[1])
			quit()
		i = fv[1][0]
		arrAddress = fv[1][1]
		addCode(['ASSIGN','#' + str(arrAddress),i,''])
		num = fv[1][-2]
		t = getTemp()
		for index in range(num) :
			addCode(['ADD','#' + str(index * 4),str(i),t])
			addCode(['ASSIGN','#0','@' + str(t),''])

	elif nonTerminal == 'x4' :
		# print "we are at " + nonTerminal
		semanticStack.append('#' + str(token[1]))

	elif nonTerminal == 'x5' :
		# print "we are at " + nonTerminal

		temp = getTemp()


		funcName = semanticStack[-1]

		if (funcName == 'output') :
			return 0

		semanticStack.pop()

		programBlock.append(['ASSIGN',returnAddress,temp,''])
		programBlockPointer = programBlockPointer + 1

		semanticStack.append(temp)


		# programBlock.append(['PRINT',baseStackPointer,'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',stackPointer,'',''])
		# programBlockPointer = programBlockPointer + 1

		programBlock.append(['SUB',baseStackPointer,'#1500',baseStackPointer])
		programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		programBlock.append(['SUB',baseStackPointer,'#8',baseStackPointer])
		programBlockPointer = programBlockPointer + 1

		addCode(['ASSIGN','@'+str(baseStackPointer),controlLink,''])

		programBlock.append(['ADD',baseStackPointer,'#8',baseStackPointer])
		programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1
		# addCode(['ADD',baseStackPointer,'#4',baseStackPointer])
		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1
		# addCode(['ASSIGN','@' + str(baseStackPointer),str(stackPointer),'',''])
		# addCode(['ADD',baseStackPointer,'#4',baseStackPointer])

		# addCode(['ADD',baseStackPointer,'#4',baseStackPointer])

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# addCode(['ADD',baseStackPointer,'#4',baseStackPointer])

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# addCode(['ADD',baseStackPointer,'#4',baseStackPointer])

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# programBlock.append(['ASSIGN',str(controlLink),t,''])
		# programBlockPointer =  programBlockPointer + 1

		# programBlock.append(['PRINT','@' + str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer =  programBlockPointer + 1

		# addCode(['ADD',baseStackPointer,'#' + str(12),baseStackPointer])
		addCode(['ASSIGN',baseStackPointer,stackPointer,''])

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		copyCode2(LOCALBASE, relAddress)
		addCode(['ASSIGN',baseStackPointer,stackPointer,''])
		addCode(['ADD',stackPointer,'#' + str(ARRAYBASE),stackPointer])
		
		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		copyCode2(ARRAYBASE, relArrAddress)
		addCode(['ASSIGN',baseStackPointer,stackPointer,''])
		addCode(['ADD',stackPointer,'#' + str(TEMPBASE),stackPointer])

		copyCode2(TEMPBASE, tempAddress - 8)	

		# programBlock.append(['PRINT',str(stackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		# programBlock.append(['PRINT',str(baseStackPointer),'',''])
		# programBlockPointer = programBlockPointer + 1

		programBlock.append(['SUB',baseStackPointer,'#12',baseStackPointer])
		programBlockPointer = programBlockPointer + 1
		addCode(['ASSIGN',baseStackPointer,stackPointer,''])


	with open('output.txt', 'w') as program :
		for item in programBlock:
			print>>program, item