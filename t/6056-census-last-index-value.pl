# kind: refused
# perl runs it: '0' (the assignment's value).
use v5.42;
my @a = (1, 2, 3);
my $x = ($#a = 0);
