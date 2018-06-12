int fibbo(int a) {
	int k;
	int l;
	int t;
	if (a == 0) {
		return 0;
	}
	else {
		if (a == 1) {
			return 1;
		}
		else {
			t = fibbo(a - 1);
			k = fibbo(a - 2);
			l = t + k;
			return l;
		}
	}
}

void main (void) {
	int a;
	int b;
	a = 2;
	b = fibbo(a);
	output(b);
}EOF