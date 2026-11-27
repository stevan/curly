# kind: refused
# perl runs it: 'a'.
use v5.42;
my @l = grep { /a/ } ("a", "b");
