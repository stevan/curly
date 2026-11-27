# kind: refused
# perl does not compile it: Missing comma after first argument to atan2 function.
use v5.42;
my $x = 3;
say atan2($x -1, 1);
