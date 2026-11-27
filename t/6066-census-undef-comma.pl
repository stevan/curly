# kind: refused
# perl runs it: 'a'.
use v5.42;
my $x = 1;
undef $x, say "a";
