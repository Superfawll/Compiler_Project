import utilities
import re

rules = utilities.getRules("grammar.txt")
gotoTable = utilities.getGotoTable("gotoTable.txt")
actionTable = utilities.getActionTable("actionTable.txt")
followSet = utilities.getFollowSet("followSets.txt")	

with open("code.c", "r") as codeFile :
	codeString = codeFile.read()
	
codeString = re.sub(r"\A\s+", "", codeString)

gotoSubSet = []
parsingStack = ['0']
utilities.tokenIterator = 0
utilities.contiguousSubString = ""
done = False
utilities.eofWatch = False
tokenPopped = False
utilities.isNum = False

utilities.root = utilities.currentNode

# These information will be used to prevent the parser from panic mode loops!

offset = 0
stackPop = 0
previousState = ''
previousToken = ''

with open("reductions.txt", "w") as reductionSequenceFile :
	while True :

		if (codeString != "" and not done):
			current = r"\A\S*(\s+|\Z)"
			utilities.contiguousSubString = re.match(current, codeString)
			if utilities.contiguousSubString :
				beginOfComment = -1
				i = 0
				while i < (len(codeString) - 1) and (not re.match(r"\A\s+", codeString[i:]) or beginOfComment >= 0 or utilities.eofWatch) :
					if codeString[i] == "/" and codeString[i + 1] == "*" and beginOfComment < 0 :
						beginOfComment = i
					if codeString[i] == "*" and codeString[i + 1] == "/" :
						if beginOfComment < 0 :
							# "ERROR, Comment end befor comment begin used!"
							quit()
							done = True
							break
						else :
							if utilities.eofWatch :
								codeString = codeString[:beginOfComment] + " " + codeString[(i + 2):]
								beginOfComment = -1
								i = -1
							else :
								utilities.contiguousSubString = re.sub(r"\s", "", codeString[:beginOfComment])
								codeString = re.sub(r"\A\s+", "", codeString[(i + 2):])
								break
					i = i + 1

				if utilities.eofWatch :
					codeString = re.sub(r"\s+", "", codeString)
					done = True

				if beginOfComment < 0 and not done :
					utilities.contiguousSubString = re.sub(r"\s", "", utilities.contiguousSubString.group())
					codeString = re.sub(current, "", codeString)

				while (utilities.contiguousSubString != "") and not done and not utilities.eofWatch :
					if not utilities.matchToken("Keyword") :
						if not utilities.matchToken("ID") :
							if not utilities.matchToken("NUM") :
								print "ERROR, String does not match any construct!"
								quit()

			else :
				print "ERROR, Code empty?!"
				quit()
				done = True

		if (utilities.tokenNum >= 1) : 
			if (not tokenPopped) :
				t = utilities.tokens[utilities.tokenIterator][0]

				# print " The stack is at: " + str(parsingStack) +  " and the input is at: " + utilities.tokens[utilities.tokenIterator][0]

				if (t[0] == 'n') : utilities.lastNum = int(utilities.tokens[utilities.tokenIterator][1])
				if (t[0] == 'i') : utilities.lastSymbol = utilities.tokens[utilities.tokenIterator][1]

				action = actionTable[t][parsingStack[-1]]
				
				# print parsingStack[-1] + " and " + t + " yields " + action

				if action == 'acc' :
					"Parse was successful!"
					break

				if action == '' :
					reductionSequenceFile.write("ERROR\n")
					# print utilities.tokens
					print "ERROR, Input and top of parser stack not compatible! Entering Panic Mode!"

					# print utilities.tokens[:utilities.tokenIterator]
					# print parsingStack

					# if stackPop >= 2 :
					# 	print "You Suck!"
					# 	quit()
					if (previousState == parsingStack[-1] and previousToken == t) : 
						offset = offset + 1
					else :
						offset = 0

					previousState = parsingStack[-1]
					previousToken = t
					
					gotoSubSet = []

					tempStackPop = stackPop

					while (True) :
						isFound = False

						for entry in utilities.nonTerminals :
							if gotoTable[entry][parsingStack[- 1]] :
								if not tempStackPop :
									isFound = True
									break
								else :
									print "Found state will not be compatible, continuing!"
									tempStackPop = tempStackPop - 1
									break

						if (len(parsingStack) <= 2) :
							print "ERROR, Stack was vacated and no proper follow found!"
							quit()

						if (not isFound) :
							temp = parsingStack.pop()
							temp = parsingStack.pop()

						else :
							break
					
					print "Proper state in the stack found! Now finding suitable input!"
					for entry in utilities.nonTerminals :
						if gotoTable[entry][parsingStack[- 1]] :
							gotoSubSet.append(entry)

					tempOffset = offset

					while tempOffset >= 1 :
						gotoSubSet.pop(0)
						tempOffset = tempOffset - 1

					if (len(gotoSubSet) == 0) :
						print "ERROR, stack has to pop more states and non-Terminals to reach a viable start!"
						# print parsingStack
						stackPop = stackPop + 1
						offset = 0
						# print stackPop
						continue
						print "ERROR, No proper state was found that does not induce recurrence in the parser! Quitting;"
						# quit()

					iterator = 0

					while (not (utilities.tokens[utilities.tokenIterator][0] in followSet[gotoSubSet[iterator]])) :
						if (iterator == len(gotoSubSet) - 1) :
							if (utilities.tokens[utilities.tokenIterator][0] == '$') :
								print "ERROR, no viable follow for any terminals found! Quitting;"
								quit()
							iterator = 0
							utilities.tokens.pop(utilities.tokenIterator)
							tokenPopped = True
							break
						else :
							iterator = iterator + 1

					if tokenPopped :
						continue
					print "Proper input in the input stream found! Continuing parsing!"

					parsingStack.append(gotoSubSet[iterator])
					parsingStack.append(gotoTable[gotoSubSet[iterator]][parsingStack[-2]])

					continue

				if action[0] == 's' :
					parsingStack.append(t)
					parsingStack.append(action[1:])

					# print utilities.tokens[utilities.tokenIterator]

					stat = utilities.semantics(utilities.tokens[utilities.tokenIterator])
					if stat != "OK!" and stat != "":
						print stat
						# utilities.root.printSubTree(0)
						quit()
 						
					utilities.tokenIterator = utilities.tokenIterator + 1
					utilities.tokenNum = utilities.tokenNum - 1
					previousState = ''
					previousToken = ''
					stackPop = 0
					# print "Input shift operation done, going to state: " + str(action[1:])
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
					if (r[0] == 'a') :
						utilities.codeGen(r[0], utilities.tokens[utilities.tokenIterator - 2])
					else  :
						utilities.codeGen(r[0], utilities.tokens[utilities.tokenIterator - 1])
					# print "Reduce operation done with rule: " + str(int(action[1:])) + " !"
			
			elif utilities.tokenNum > 1 :	
				tokenPopped = False
				iterator = 0
				while (not (utilities.tokens[utilities.tokenIterator][0] in followSet[gotoSubSet[iterator]])) :
					if (iterator == len(gotoSubSet) - 1) :
						if (utilities.tokens[utilities.tokenIterator][0] == '$') :
							print "ERROR, no viable follow for any terminals found! Quitting;"
							quit()
						iterator = 0
						utilities.tokens.pop(utilities.tokenIterator)
						tokenPopped = True
						break
					else :
						iterator = iterator + 1

				if tokenPopped :
					continue
				# "//////Proper input in the input stream found! Continuing parsing!"

				parsingStack.append(gotoSubSet[iterator])
				parsingStack.append(gotoTable[gotoSubSet[iterator]][parsingStack[-2]])

				continue
			
# utilities.root.printSubTree(0)
# print "\n\n"
# print utilities.functions

# utilities.root.printSubTree(0)
# print utilities.functions

# print utilities.programBlock

with open('program.txt', 'w') as program :
	for item in utilities.programBlock:
  		print>>program, item

# print "\n"
# print str(utilities.tokens) + "\nThis is the understood language flow of the program!"


