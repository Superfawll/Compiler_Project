import re

ID = r"([A-Za-z]([A-Za-z]|[0-9])*)"
NUM = r"((\+|-)?([0-9])+)"
keyword1 = r"(EOF|int|void|if|else|while|return)"
keyword2 = r"(;|\[|\]|\(|\)|\{|\}|,|=|<|==|\+|\*|-)"
nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','t','u','s','w1','y','c','d','h','x2','x4','x7','x5','x6','k','x9','o','m','r1','p','w2','j','b','a','x3','x1','x8','l']
terminals = ['(',')','*','+',',','-',';','<','=','[',']','e','f','g','i','n','q','r','v','w','z','{','}','$']

contiguousSubString = ""
tokens = []
eofWatch = False
tokenNum = 0
isNum = False

# class Node:
# 	def __init__(self):
#     	self.returned = False
#     	self.children = []

class BlockNode:
    def __init__(self, fun, n, s, p):
    	self.function = fun
        self.name = n
        self.symbolTable = s
        self.parent = p
        self.children = []
        # self.root = Node()
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

    def checkReturned():
    	return


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
relAddress = 0
relParAddress = -4
relArrAddress = 1300
tempAddress = 301
currentBlockNode = BlockNode(True, "", {}, None)
functions = {'output':['void', -1, {'x': [-4, -1, 1, False]}]}

semanticStack = []
programBlock = []
programBlock.append(['ASSIGN','#200',500,''])
programBlockPointer = 1
tokenIterator = 0
lastFunc = ''
isFirstFunc = False

# tempAddr = 500

mapping = { "else": "e",
			"if": "f",
			"int": "g",
			"return": "r",
			"void": "v",
			"while": "w",
			"EOF":"z" }	

numSignIndicator = ['[','(','*','=',',','+','-','<','q','e','r']


def getTemp():
	global tempAddress

	a = tempAddress
	tempAddress = tempAddress + 1
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
			if len(tokens) > 1 and tokens[len(tokens) - 1][0] == "=" and sKey == "=" :
				tokens[len(tokens) - 1] = ('q','==')
			else :
				if sKey in mapping.keys() :
					tokens.append((mapping[sKey], sKey))
					tokenNum = tokenNum + 1
				else :
					tokens.append((sKey, sKey))
					tokenNum = tokenNum + 1
			contiguousSubString = re.sub(keyword, "", contiguousSubString)
			if sKey == "EOF" :
				eofWatch = True
				tokens.append(('$', 'none'))
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
			tokens.append((tag, matched))
			tokenNum = tokenNum + 1
			contiguousSubString = re.sub(pattern, "", contiguousSubString)
			return True
		else :
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
	followSet = {'A':'','B':'','C':'','D':'','E':'','F':'','G':'','H':'','I':'','J':'','K':'','L':'','M':'','N':'','O':'','P':'','Q':'','R':'','S':'','T':'','U':'','V':'','W':'','X':'','Y':'','Z':'','x':'','y':''}
	keyList = followSet.keys();
	keyList.sort()
	with open(file, "r") as fSetFile :
		for i in keyList :
			followSet[i] = fSetFile.readline().replace('\n','')

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
	global relParAddress
	global relArrAddress
	global tempAddress
	global lastSymbol
	global lastNum
	global lastFunc

	if state1 == 0:
		state1 = 1 if (t == "g" or t == "v") else (9 if t == "z" else 0)

	elif state1 == 1:
		state1 = 2 if t == "i" else -1

	elif state1 == 2: 
		# Checking whether main is the last function declaration or not!
		if t == "(":
			if "main" in functions.keys() and lastSymbol != "main":
				return "\'{}\'' Is Defined After \'main\'".format(lastSymbol)
			# Checking whether the function defined has a duplicate name as another function or not!
			if lastSymbol in functions.keys():
				return "Duplicate Function Definition: \'{}\'' Already Exists!".format(lastSymbol)
			else:
				functions[lastSymbol] = [lastType, -1]
			# Inserting the new identifier inside of the symbol table linked-list
			lastFunc = lastSymbol
			node = BlockNode(True, lastSymbol, {}, currentBlockNode)
			currentBlockNode.children.append(node)
			currentBlockNode = node
			# currentBlockNode.root.returned = False if lastType == "int" else True
			relAddress = 0
			relParAddress = -4
			relArrAddress = 1300
			tempAddress = 301
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
			currentBlockNode = node
			scopeCounter = scopeCounter + 1
		elif t == "}":
			# currentBlockNode.checkReturned()
			if scopeCounter == 0:
				# if not currentBlockNode.root.returned:
				# 	return "Function \'{}\' Has Not Retured A Value".format(currentBlockNode.name)
				state1 = 0
			else:
				scopeCounter = scopeCounter - 1
			currentBlockNode = currentBlockNode.parent
		elif t == "w" or t == "f":
			state1 = 6
			# node = Node()
			# currentBlockNode.curNode.children.append([node])
			# currentBlockNode.curNode = node
		elif t == "e":
			state1 = 8
			# node = Node()
			# currentBlockNode.curNode.children[-1].append(node)
			# currentBlockNode.curNode = node
		# elif t == "r":
		# 	currentBlockNode.root.returned = True

	elif state1 == 6:
		state1 = 7 if t == "(" else -1

	elif state1 == 7:
		if t == ")":
			state1 = 8

	elif state1 == 8:
		if t == "{":
			node = BlockNode(False, currentBlockNode.name, {}, currentBlockNode)
			currentBlockNode.children.append(node)
			currentBlockNode = node
			state1 = 5
			scopeCounter = scopeCounter + 1
		elif t == "f" or t == "w":
			state1 = 6
			# node = Node()
			# currentBlockNode.curNode.children.append([node])
			# currentBlockNode.curNode = node
		# elif t == "e":
			# node = Node()
			# currentBlockNode.curNode.children[-1].append(node)
			# currentBlockNode.curNode = node
		elif t != "e":
			state1 = 5
			# if t == "r":
			# currentBlockNode.curNode.returned = True

	return "" if state1 == -1 else "OK!"


def addVars(t):
	global state2
	global lastType
	global currentBlockNode
	global lastSymbol
	global lastNum
	global isArray
	global relAddress
	global relParAddress
	global relArrAddress

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
				return "Duplicate Variable Definition: \'{}\'' Already Exists In This Scope!".format(lastSymbol)
			if lastType == "void":
				return "Variable \'{}\' Can Not Be Defined Of Type \'void\'".format(lastSymbol)

			aa = -1
			if state1 == 3 or state1 == 4:
				ra = relParAddress
				relParAddress = relParAddress - 4
			else:
				ra = relAddress
				relAddress = relAddress + 4
				if isArray:
					if lastNum < 1:
						return "Can Not Define Array Of Size {}!".format(lastNum)
					else:
						aa = relArrAddress
						relArrAddress = relArrAddress + 4 * lastNum
			currentBlockNode.setSymbol(lastSymbol, ra, aa, lastNum if isArray else 1, isArray)

			state2 = 0
			if t == ")":
				functions[currentBlockNode.name].append(currentBlockNode.symbolTable.copy())
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


def codeGen(nonTerminal, token):
	global programBlockPointer
	global programBlock
	global semanticStack
	global isFirstFunc
	global lastFunc

	# print currentBlockNode.symbolTable

	if nonTerminal == 'a' :
		if (not isFirstFunc) : 
			programBlock.append('')
			semanticStack.append(programBlockPointer)
			programBlockPointer = programBlockPointer + 1
			isFirstFunc = True
		if token[1] == 'main' :
			pointer = semanticStack.pop()
			programBlock[pointer] = ['JP',programBlockPointer,'','']
		functions[token[1]][1] = programBlockPointer
	
	elif nonTerminal == 'b' :
		# print semanticStack
		# print programBlock
		semanticStack.pop()
	
	elif nonTerminal == 'h' :
		semanticStack.append(programBlockPointer)
		# print "The semantic stack is at: " + str(semanticStack)
		programBlockPointer = programBlockPointer + 1
		programBlock.append('')
	
	elif nonTerminal == 'd' :

		programBlock[semanticStack[-1]] = ['JPF',semanticStack[-2],programBlockPointer + 1,'']
		semanticStack.pop()
		semanticStack.pop()
		semanticStack.append(programBlockPointer)
		programBlockPointer = programBlockPointer + 1
		programBlock.append('')
	
	elif nonTerminal == 'c' :
		# print semanticStack[-1]
		# print programBlock[semanticStack[-1]]
		programBlock[semanticStack[-1]] = ['JP',programBlockPointer,'','']
		semanticStack.pop()
	
	elif nonTerminal == 'j' :
		semanticStack.append(programBlockPointer)
	
	elif nonTerminal == 'o' :
		semanticStack.append(programBlockPointer)
		programBlockPointer = programBlockPointer + 1
		programBlock.append('')
	
	elif nonTerminal == 'l' :
		programBlock[semanticStack[-1]] = ['JPF',semanticStack[-2],programBlockPointer + 1,'']
		# print programBlock[semanticStack[-1]]
		programBlock.append(['JP',semanticStack[-3],'',''])
		programBlockPointer = programBlockPointer + 1
		semanticStack.pop()
		semanticStack.pop()
		semanticStack.pop()
	
	elif nonTerminal == 'k' :
		semanticStack.append(programBlockPointer)
	
	elif nonTerminal == 'm' :
		# Return address of the function is pushed at the begining, so just assigning the return value to the return address!
		# programBlock.append(['ASSIGN',semanticStack[-1],semanticStack[-2],''])
		programBlockPointer = programBlockPointer + 1
		semanticStack.pop()
		semanticStack.pop()
		semanticStack.append(programBlockPointer)
	
	elif nonTerminal == 'w2' :
		programBlock.append(['ASSIGN',semanticStack[-1],semanticStack[-2],''])
		programBlockPointer = programBlockPointer + 1
		semanticStack.pop()
		result = semanticStack.pop()
		semanticStack.append(result)
	
	elif nonTerminal == 'r1' :
		temp = getTemp()
		temp1 = getTemp()
		i = (findVar(token[1], currentBlockNode))[1][0]
		semanticStack.append(programBlockPointer)
		programBlock.append(['ASSIGN','#' + str(i),temp,''])
		programBlock.append(['ADD',temp,500,temp1])
		programBlockPointer = programBlockPointer + 2
		semanticStack.append('@' + str(temp1))
	
	elif nonTerminal == 'p' :
		tempAddr1 = getTemp()
		tempAddr2 = getTemp()
		gett2 = getTemp()
		pointer = semanticStack[-3]
		temp = semanticStack.pop()
		semanticStack.pop()
		wrongAddresses = programBlock[pointer]
		wrongAddresses[1] = wrongAddresses[1].replace('#','')
		programBlock[pointer + 1] = ['ADD',500,wrongAddresses[2],tempAddr1]
		programBlock.append(['ADD',tempAddr1,temp,tempAddr2])
		semanticStack.append('@' + str(tempAddr2))
		programBlockPointer = programBlockPointer + 1
	
	elif nonTerminal == 's' :
		temp = getTemp()
		firstOperand = semanticStack.pop()
		operation = semanticStack.pop()
		secondOperand = semanticStack.pop()
		programBlock.append(['EQ',firstOperand,secondOperand,temp] if (operation == 'equal') else (['LT',secondOperand,firstOperand,temp] if operation == 'less' else '')) # TODO:Addressing!!!!!!!!
		programBlockPointer = programBlockPointer + 1
		semanticStack.append(temp)
	
	elif nonTerminal == 't' :
		semanticStack.append('less')
	
	elif nonTerminal == 'u' :
		semanticStack.append('equal')
	
	elif nonTerminal == 'x1' :
		temp = getTemp()
		firstOperand = semanticStack.pop()
		operation = semanticStack.pop()
		secondOperand = semanticStack.pop()
		programBlock.append(['ADD',firstOperand,secondOperand,temp] if operation == 'add' else (['SUB',secondOperand,firstOperand,temp] if operation == 'sub' else '')) # TODO:Addressing!!!!!!!!
		programBlockPointer = programBlockPointer + 1
		semanticStack.append(temp)
	
	elif nonTerminal == 'w1' :
		semanticStack.append('add')
	
	elif nonTerminal == 'x2' :
		semanticStack.append('sub')
	
	# elif nonTerminal == 'x5' :
	
	elif nonTerminal == 'x6' :
		temporary = getTemp()
		argsList = []
		while not semanticStack[-1] == '(' :
			argsList.append(semanticStack.pop())
		semanticStack.pop()
		
		if semanticStack[-1] == 'output' :
			programBlock.append(['PRINT',argsList[0],'',''])
			programBlockPointer = programBlockPointer + 1
			return 0
		else :
			funcID = semanticStack[-1]
			print functions[funcID]
			if (not len(argsList) == len(functions[funcID])):
				print "Parameter count does not match!" + str(argsList)
		
		programBlock.append(['ASSIGN',500,199,''])
		programBlockPointer = programBlockPointer + 1
		
		programBlock.append(['ADD',500,'#1804',temporary])
		programBlockPointer = programBlockPointer + 1
		programBlock.append(['ASSIGN',temporary,500,''])
		# programBlock.append(['PRINT',500,'',''])
		programBlockPointer = programBlockPointer + 1
		
		for iterator in range(len(argsList)) :
			if (not argsList[2] == 'arr') :
				programBlock.append(['ASSIGN',argsList[iterator],'@500',''])
				programBlockPointer = programBlockPointer + 1
				programBlock.append(['ADD',500,'#4',temporary])
				programBlock.append(['ASSIGN',temporary,500,''])
				programBlockPointer = programBlockPointer + 2
			else :
				programBlock.append(['ASSIGN',argsList[iterator].replace('@',''),'@500',])
				programBlockPointer = programBlockPointer + 1
				programBlock.append(['ADD',500,'#4',temporary])
				programBlock.append(['ASSIGN',temporary,500,''])
				programBlockPointer = programBlockPointer + 2

		programBlock.append(['ASSIGN','#' + str(programBlockPointer + 4),'@500',''])
		programBlockPointer = programBlockPointer + 1
		programBlock.append(['ADD',500,'#4',temporary])
		programBlock.append(['ASSIGN',temporary,500,''])
		programBlockPointer = programBlockPointer + 2

		jumpAddress = functions[funcID][1]

		programBlock.append(['JP',jumpAddress,'',''])
		programBlockPointer = programBlockPointer + 1
	
	elif nonTerminal == 'x7' :
		temp = getTemp()
		firstOperand = semanticStack.pop()
		secondOperand = semanticStack.pop()
		programBlock.append(['MULT',firstOperand,secondOperand,temp]) # TODO:Addressing!!!!!!!!
		programBlockPointer = programBlockPointer + 1
		semanticStack.append(temp)
	
	elif nonTerminal == 'x8' :
		temporary = getTemp()
		if (not lastFunc == 'main') :
			programBlock.append(['SUB',500,'#4',temporary])
			programBlockPointer = programBlockPointer + 1
			
			programBlock.append(['ASSIGN',199,500,''])
			programBlockPointer = programBlockPointer + 1

			programBlock.append(['JP',92,'',''])
			programBlockPointer = programBlockPointer + 1
	
	elif nonTerminal == 'x9' :
		semanticStack.append(token[1])
		semanticStack.append('(')

	elif nonTerminal == 'V' :
		semanticStack.pop(-2)

	elif nonTerminal == 'x3' :
		i = (findVar(token[1], currentBlockNode))[1][0]
		arrAddress = (findVar(token[1], currentBlockNode))[1][1]
		programBlock.append(['ASSIGN','#' + str(arrAddress),i,''])
		programBlockPointer =  programBlockPointer + 1

	elif nonTerminal == 'x4' :
		semanticStack.append('#' + str(token[1]))





