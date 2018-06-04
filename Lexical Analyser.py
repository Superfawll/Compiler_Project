import re

comment = r"(/\*.*\*/\s*)"
ID = r"([A-Za-z]([A-Za-z]|[0-9])*)"
NUM = r"((\+|-)?([0-9])+)"
keyword1 = r"(EOF|int|void|if|else|while|return)"
keyword2 = r"(;|\[|\]|\(|\)|\{|\}|,|=|<|==|\+|\*|-)"

mapping = { "else": "e",
			"if": "f",
			"int": "g",
			"return": "r",
			"void": "v",
			"while": "w",
			"EOF":"z" }	

tokens = []
symbolTable = {}

with open("code.c", "r") as F :
	str = F.read()

str = re.sub(comment + r"|(\A(\s)+)", "", str)
done = False
while (str != "") and (not done) :
	current = r"\A\S*(\s+|(EOF))"
	s = re.match(current, str)
	if s :
		s = s.group()
		str = re.sub(current, "", str)

		while (s != "") and (not done) :

			keyword = r"\A" + "(" + keyword2 + "|(" + keyword1 + "(?!" + "[A-Za-z0-9]" + ")))"
			sKey = re.match(keyword, s)
			if sKey :
				sKey = sKey.group()
				if len(tokens) > 1 and tokens[len(tokens) - 1] == "=" and sKey == "=" :
					tokens[len(tokens) - 1] = "q"
				else :
					if sKey in mapping.keys() :
						tokens.append(mapping[sKey])
					else :
						tokens.append(sKey)
				s = re.sub(keyword, "", s)
				if sKey == "EOF" :
					done = True

			else :
				sID = re.match(r"\A" + ID, s)
				if sID :
					sID = sID.group()
					tokens.append("i")
					symbolTable[sID] = "i"
					s = re.sub(r"\A" + ID, "", s)

				else :
					sNUM = re.match(r"\A" + NUM, s)
					if sNUM :
						sNUM = sNUM.group()
						tokens.append("n")
						symbolTable[sNUM] = "n"
						s = re.sub(r"\A" + NUM, "", s)

					else :
						print "ERROR"
						done = True

			s = re.sub(r"\s", "", s)
	else :
		print "ERROR"
		done = True

if str != "" :
	print "ERROR"

with open("results/tokens.txt", "w") as F :
	for t in tokens :
		F.write(t + "\n")

with open("results/symbol table.txt", "w") as F :
	for k in symbolTable.keys() :
		F.write(k + "\t" + symbolTable[k] + "\n")

		