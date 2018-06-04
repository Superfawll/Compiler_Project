# Parser, C Minus grammar

# Extracting rules from rules file
rules = []
with open("grammar.txt", "r") as F :
	for i in range(55) :
		sl = F.readline().split("\t")
		rules.append([sl[0], (len(sl[1]) - 1) * 2])

# Extracting goto table from a file as a string to be parsed later

nonTerminals = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','x','y']
with open("gotoTable.txt", "r") as F :
	string = F.read()

# Extracting followe set from a file as a dictionary for panic mode

followSet = {'A':'','B':'','C':'','D':'','E':'','F':'','G':'','H':'','I':'','J':'','K':'','L':'','M':'','N':'','O':'','P':'','Q':'','R':'','S':'','T':'','U':'','V':'','W':'','X':'','Y':'','Z':'','x':'','y':''}

keyList = followSet.keys();
keyList.sort()
with open("followSets.txt", "r") as fSet :
	for i in keyList :
		 fString= fSet.readline()
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
with open("actionTable.txt", "r") as F:
	string = F.read()

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

with open("results/tokens.txt", "r") as F :
	tokens = F.read().split("\n")
tokens.append("$")

gotoSubTable = []

# Starting the parsing mechanism

SS = ['0']
n = 0

# These information will be used to prevent the parser from panic mode loops!

offset = 0
previousState = ''
previousToken = ''

# Streaming reduction series to output file: reductions.txt

with open("results/reductions.txt", "w") as F :

	while True :
		t = tokens[n]
		action = actionTable[t][SS[-1]]
		print SS[-1] + " and " + t + " yields " + action
		
		if (previousState == SS[-1] and previousToken == t) : 
			offset = offset + 1
		else :
			offset = 0

		previousState = SS[-1]
		previousToken = t

		if action == 'acc' :
			print "Parse was successful!"
			break
		if action == '' :
			F.write("ERROR")


			print "ERROR, Input and top of parser stack not compatible! Entering Panic Mode!"

			# Panic mode!
			
			gotoSubTable = []

			while (True) :
				isFound = False
				for entry in nonTerminals :
					# print entry + " and " + SS[-1]
					if gotoTable[entry][SS[- 1]] :
						isFound = True
						break

				if (len(SS) <= 2) :
					print "ERROR, Stack was vacated and no proper follow found!"
					quit()
				if (not isFound) :
					SS.pop()
					SS.pop()
				else :
					break
			
			print "Proper state in the stack found! Now finding suitable input!"
			for entry in nonTerminals :
				if gotoTable[entry][SS[- 1]] :
					gotoSubTable.append(entry)

			tempOffset = offset

			while tempOffset >= 1 :
				gotoSubTable.pop(0)
				tempOffset = tempOffset - 1

			# print gotoSubTable

			iterator = 0
			while (not (tokens[n] in followSet[gotoSubTable[iterator]])) :
				if (iterator == len(gotoSubTable) - 1) :
					iterator = 0
					tokens.pop(n)
				else :
					iterator = iterator + 1
			print "Proper input in the input stream found! Continuing parsing!"

			SS.append(gotoSubTable[iterator])
			SS.append(gotoTable[gotoSubTable[iterator]][SS[-2]])

			continue

		if action[0] == 's' :
			SS.append(t)
			SS.append(action[1:])
			n = n + 1
			print "Input shift operation done!"
		if action[0] == 'r' :
			F.write(action[1:] + "\n")
			r = rules[int(action[1:]) - 1]
			if r[1] > 0 :
				l = len(SS) - r[1] - 1
				if l > 0 :
					SS = SS[:(l + 1)]
				else :
					SS = ['0']
			SS.append(r[0])
			SS.append(gotoTable[r[0]][SS[-2]])
			print "Reduce operation done with rule: " + str(int(action[1:])) + " !"

print str(tokens) + " This is the understood language flow of the program!"


