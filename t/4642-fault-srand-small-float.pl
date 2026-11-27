# kind: fault
# perl warns: Integer overflow in srand (T479).
use v5.42;
srand(1e-5);
