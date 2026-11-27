# kind: refused
# perl dies: not a SCALAR reference; a dereference without braces is cut, in a string too (D108).
use v5.42;
my $x = 3;
say "$$x";
