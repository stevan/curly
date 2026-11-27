# kind: fault
# perl prints 18446744073709551615 (T474).
use v5.42;
say -1 & 1;
say -1 | 0;
