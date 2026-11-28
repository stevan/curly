# kind: fault
# perl prints the one byte of a capital E with an acute, with no use open, and warns of nothing; the language faults (D39).
use v5.42;
say uc(chr(0xE9));
