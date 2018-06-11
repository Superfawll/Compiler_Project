/*int fibbo(int a) {
	if (a == 0) {return 0;}
	else if (a == 1) {return 1;}
	else {return fibbo(a - 1) + fibbo(a - 2);}
}*/

int a

int func(int b[]){
	int x[11];
	int a;
	output(b[1]);
	a = 9;
	b[1] = 13;
	
	while(0<a){
		x[a] = 9 - a;
		a = a - 1;
		output(x[a]);
	}
	/*a = 9;
	while (0<a){
		x[a] = 9 - a;
		a = a - 1;
		output(x[a]);
		a = a - 1;
	}
*/

	/*if (x[1] == 1) {
		return 10;
	}
	else {
		return 5;
	}*/
	output(b[1]);
	return a;
}


int main(void){
	int v[2];
	int a;
	int b;
	a = 5;
	v[1] = 15;
	output(v[1]);
	b = 2;
	output(func(v));

	return 0;
} EOF


