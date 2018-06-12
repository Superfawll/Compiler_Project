int fibbo(int a) {
	if (a == 0) {
		return 0;
	}
	else {
		if (a == 1) {
			return 1;
		}
		else {
			return fibbo(a - 1) + fibbo(a - 2);
		}
	}
}


void main (void) {
	output(fibbo(15));
}EOF