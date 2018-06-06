import re

ID = r"([A-Za-z]([A-Za-z]|[0-9])*)"
NUM = r"((\+|-)?([0-9])+)"
keyword1 = r"(EOF|int|void|if|else|while|return)"
keyword2 = r"(;|\[|\]|\(|\)|\{|\}|,|=|<|==|\+|\*|-)"
nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','y']
terminals = ['$',')','(','*','+',',','-',';','<','=','[',']','e','f','g','i','n','q','r','v','w','z','{','}']

contiguousSubString = ""
tokens = []
symbolTable = {}
eofWatch = False
tokenNum = 0
isNum = False

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
	global symbolTable
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
			symbolTable[matched] = tag
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

