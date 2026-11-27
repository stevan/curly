# kind: refused
# perl warns: Possible precedence problem on bitwise & operator (T489).
use v5.42;
my $y = 3;
say 6 & $y == 3;
