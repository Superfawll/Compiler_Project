# Parser, C Minus grammar

# Extracting rules from rules file
rules = []
with open("grammar.txt", "r") as grammarFile :
	for i in range(55) :
		rule = grammarFile.readline().split("\t")
		rules.append([rule[0], (len(rule[1]) - 1) * 2])

# Extracting goto table from a file as a string to be parsed later

nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','y']
with open("gotoTable.txt", "r") as gotoTableFile :
	string = gotoTableFile.read()

# Extracting followe set from a file as a dictionary for panic mode

followSet = {'A':'','B':'','C':'','D':'','E':'','F':'','G':'','H':'','I':'','J':'','K':'','L':'','M':'','N':'','O':'','P':'','Q':'','R':'','S':'','T':'','U':'','V':'','W':'','X':'','Y':'','Z':'','x':'','y':''}

keyList = followSet.keys();
keyList.sort()
with open("followSets.txt", "r") as fSet :
	for i in keyList :
		 fString = fSet.readline()
		 followSet[i] = fString.replace('\n','')

# Goto Table extraction into a dic

gotoTable = {}
for i in nonTerminals :
	gotoTable[i] = {}

iterator = 0
for i in range(0, 96) :
	for j in nonTerminals :
		gotoTable[j][str(i)] = string[(iterator * 4) + i * 113: ((iterator + 1) * 4 + i * 113)].replace(' ', '')
		iterator = iterator + 1
	iterator = 0	


terminals = ['$',')','(','*','+',',','-',';','<','=','[',']','e','f','g','i','n','q','r','v','w','z','{','}']
with open("actionTable.txt", "r") as actionTableFile:
	string = actionTableFile.read()

# Action Table extraction into a dic

actionTable = {}
for i in terminals :
	actionTable [i] = {}

iterator = 0
for i in range(0, 96) :
	for j in terminals :
		actionTable[j][str(i)] = string[(iterator * 4) + i * 97: ((iterator + 1) * 4 + i * 97)].replace(' ', '')
		iterator = iterator + 1
	iterator = 0	

# Obtaining the stream of input tokens

with open("results/tokens.txt", "r") as tokensFile :
	tokens = tokensFile.read().split("\n")
tokens.append("$")

gotoSubSet = []

# Starting the parsing mechanism

parsingStack = ['0']
tokenIterator = 0

# These information will be used to prevent the parser from panic mode loops!

offset = 0
previousState = ''
previousToken = ''

# Streaming reduction series to output file: reductions.txt

with open("results/reductions.txt", "w") as reductionSequenceFile :

	while True :
		t = tokens[tokenIterator]
		action = actionTable[t][parsingStack[-1]]
		print parsingStack[-1] + " and " + t + " yields " + action
		
		if (previousState == parsingStack[-1] and previousToken == t) : 
			offset = offset + 1
		else :
			offset = 0

		previousState = parsingStack[-1]
		previousToken = t

		if action == 'acc' :
			print "Parse was successful!"
			break

		if action == '' :
			reductionSequenceFile.write("ERROR")
			print "ERROR, Input and top of parser stack not compatible! Entering Panic Mode!"

			# Panic mode!
			
			gotoSubSet = []

			while (True) :
				isFound = False
				for entry in nonTerminals :
					if gotoTable[entry][parsingStack[- 1]] :
						isFound = True
						break

				if (len(parsingStack) <= 2) :
					print "ERROR, Stack was vacated and no proper follow found!"
					quit()
				if (not isFound) :
					parsingStack.pop()
					parsingStack.pop()
				else :
					break
			
			print "Proper state in the stack found! Now finding suitable input!"
			for entry in nonTerminals :
				if gotoTable[entry][parsingStack[- 1]] :
					gotoSubSet.append(entry)

			tempOffset = offset

			while tempOffset >= 1 :
				gotoSubSet.pop(0)
				tempOffset = tempOffset - 1

			if (len(gotoSubSet) == 0) :
				print "ERROR, No proper state was found that does not induce recurrence in the parser! Quitting;"
				quit()

			iterator = 0
			while (not (tokens[tokenIterator] in followSet[gotoSubSet[iterator]])) :
				if (iterator == len(gotoSubSet) - 1) :
					iterator = 0
					tokens.pop(tokenIterator)
				else :
					iterator = iterator + 1
			print "Proper input in the input stream found! Continuing parsing!"

			parsingStack.append(gotoSubSet[iterator])
			parsingStack.append(gotoTable[gotoSubSet[iterator]][parsingStack[-2]])

			continue

			# Panic mode!

		if action[0] == 's' :
			parsingStack.append(t)
			parsingStack.append(action[1:])
			tokenIterator = tokenIterator + 1
			print "Input shift operation done, going to state: " + str(action[1:])
		if action[0] == 'r' :
			reductionSequenceFile.write(action[1:] + "\n")
			r = rules[int(action[1:]) - 1]
			if r[1] > 0 :
				l = len(parsingStack) - r[1] - 1
				if l > 0 :
					parsingStack = parsingStack[:(l + 1)]
				else :
					parsingStack = ['0']
			parsingStack.append(r[0])
			parsingStack.append(gotoTable[r[0]][parsingStack[-2]])
			print "Reduce operation done with rule: " + str(int(action[1:])) + " !"

print str(tokens) + "\nThis is the understood language flow of the program!"


