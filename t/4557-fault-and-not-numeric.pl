# kind: fault
# perl warns: Argument "abc" isn't numeric in numeric bitwise and.
use v5.42;
say "abc" & 1;
