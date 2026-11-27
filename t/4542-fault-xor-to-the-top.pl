# kind: fault
# perl prints 18446744073709551615.
use v5.42;
say 1 ^ -2;
