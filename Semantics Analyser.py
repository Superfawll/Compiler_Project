var = [{}]
state1 = 0
s1Ind = 0
state2 = 0
lastSize = 0


def nextState1(t):
	global s1Ind
	global state1
	global var

	if state1 == 0:
		state1 = 1 if (t == "g" or t == "v") else (5 if t == "z" else 0)

	else if state1 == 1:
		state1 = 2 if t == "i" else -1

	else if state1 == 2: 
		if t == "(":
			var.append({})
			state1 = 3
		else:
			state1 = 0

	else if state1 == 3:
		if t == ")":
			var.pop()
			state1 = 4

	else if state1 == 4:
		if t == "{":
			var.append({})
			state1 = 6
			s1Ind = 0
		else: state1 = -1

	else if state1 == 6:
		if t == "{":
			var.append({})
			s1Ind = s1Ind + 1
		else if t == "}":
			var.pop()
			if s1Ind == 0:
				state1 = 0
			else:
				s1Ind = s1Ind - 1
		else:
			state1 = 7 if (t == "f" or t == "w") else (9 if t == "e" else 6)

	else if state1 == 7:
		state1 = 8 if t == "(" else -1

	else if state1 == 8:
		if t == ")":
			state1 = 9

	else if state1 == 9:
		if t == "{":
			var.append({})
			state1 = 6
			s1Ind = s1Ind + 1
		else if t == "f" or t == "w":
			state1 = 7
		else if t != "e":
			var.append({})
			state1 = 10 # if this is the case and t is ";", consider the token again

	else if state1 == 10:
		if t == ";":
			var.pop()
			state1 = 6

	return "Syntax Error!" if state == -1 else "OK!"


def nextState2(t, symbol, address, num):
	global state2
	global lastSize
	global var

	if state == 0:
		if t == "g" or t == "v":
			state = 1
			lastSize = 32 if t == "g" else 1

	else if state == 1:
		state = 2 if t == "i" else -1

	else if state == 2:
		if t == "(":
			state = 0
		else if t == "[":
			state = 3
		else if t == ";" or t == ")" or t == ",":
			if symbol in var[-1]:
				return "Duplicate Variable Definition!"
			var[-1][symbol] = [address, lastSize]
			state = 0
		else:
			state = -1

	else if state == 3:
		if t == "n":
			lastSize = lastSize * num
			state = 4
		else:
			state = -1

	else if state == 4:
		state = 2 if t == "]" else -1

	return "Syntax Error!" if state == -1 else "OK!"












