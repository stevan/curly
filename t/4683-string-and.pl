# kind: refused
# perl prints 10: the string bitwise and (T46).
use v5.42;
say "12" &. "10";
