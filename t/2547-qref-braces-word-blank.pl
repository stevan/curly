# kind: refused
# perl runs it: '1\n'.
use v5.42;
my @name = (1);
say "@{ name }";
