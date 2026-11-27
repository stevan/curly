# kind: refused
# perl warns: Possible precedence problem on bitwise ^ operator (T489).
use v5.42;
my $z = 6;
say $z ^ $z <=> 1;
