# kind: fault
# perl warns: Integer overflow in srand, the string being 1e+15.
use v5.42;
srand(999999999999999);
srand(1e15);
