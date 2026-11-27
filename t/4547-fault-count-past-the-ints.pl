# kind: fault
# perl clamps the count, and prints 0.
use v5.42;
say 1 << 1e19;
