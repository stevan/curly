# kind: refused
# perl warns: Use of "rand" without parentheses is ambiguous (T485).
use v5.42;
my $x = rand + 1;
