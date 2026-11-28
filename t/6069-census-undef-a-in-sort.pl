# kind: refused
# perl dies: Modification of a read-only value attempted.
use v5.42;
my @a = sort { undef $a; 0 } (2, 1);
