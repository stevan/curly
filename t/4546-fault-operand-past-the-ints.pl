# kind: fault
# perl takes 1e19 as the unsigned integer, and prints 0.
use v5.42;
say 1e19 & 1;
