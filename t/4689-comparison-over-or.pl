# kind: refused
# perl warns: Possible precedence problem on bitwise | operator (T489).
use v5.42;
my $y = 3;
say $y < 3 | 6;
