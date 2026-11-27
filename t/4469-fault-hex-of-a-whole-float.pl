# kind: fault
# perl makes the string 1e+15, and stops at the plus (D36).
use v5.42;
say hex(1e15);
