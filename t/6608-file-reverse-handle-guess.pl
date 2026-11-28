# kind: refused
# perl does not compile it: Missing comma after first argument to reverse function.
use v5.42;
my $x = 5;
my @r = reverse($x -1, 2);
