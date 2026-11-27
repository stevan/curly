# kind: fault
# perl prints 18446744073709551614.
use v5.42;
say -1 >> 0;
