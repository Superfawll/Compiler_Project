import re
import utilities

with open("code.c", "r") as F :
	codeString = F.read()

utilities.matchedPortion = ""

codeString = re.sub(r"\A\s+", "", codeString)
done = False
utilities.eofWatch = False
while codeString != "" and not done :
	current = r"\A\S*(\s+|\Z)"
	utilities.matchedPortion = re.match(current, codeString)
	if utilities.matchedPortion :
		beginOfComment = -1
		i = 0
		while i < (len(codeString) - 1) and (not re.match(r"\A\s+", codeString[i:]) or beginOfComment >= 0 or utilities.eofWatch) :
			if codeString[i] == "/" and codeString[i + 1] == "*" and beginOfComment < 0 :
				beginOfComment = i
			if codeString[i] == "*" and codeString[i + 1] == "/" :
				if beginOfComment < 0 :
					print "ERROR1"
					done = True
					break
				else :
					if utilities.eofWatch :
						codeString = codeString[:beginOfComment] + " " + codeString[(i + 2):]
						beginOfComment = -1
						i = -1
					else :
						utilities.matchedPortion = re.sub(r"\s", "", codeString[:beginOfComment])
						codeString = re.sub(r"\A\s+", "", codeString[(i + 2):])
						break
			i = i + 1
		if utilities.eofWatch :
			codeString = re.sub(r"\s+", "", codeString)
			done = True

		if beginOfComment < 0 and not done :
			utilities.matchedPortion = re.sub(r"\s", "", utilities.matchedPortion.group())
			codeString = re.sub(current, "", codeString)
		while (utilities.matchedPortion != "") and not done and not utilities.eofWatch :
			if not utilities.matchToken("Keyword") :
				if not utilities.matchToken("ID") :
					if not utilities.matchToken("NUM") :
						print "ERROR2"
						done = True

	else :
		print "ERROR3"
		done = True

if codeString != "" :
	print "ERROR4"

with open("results/tokens.txt", "w") as tokensFile :
	for t in utilities.tokens :
		tokensFile.write(t + "\n")

with open("results/symbol table.txt", "w") as symTabFile :
	for k in utilities.symbolTable.keys() :
		symTabFile.write(k + "\t" + utilities.symbolTable[k] + "\n")

		