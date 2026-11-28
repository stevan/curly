# kind: refused
# perl does not compile it: Missing comma after first argument to die function.
use v5.42;
my $x = 5;
die $x -1;
