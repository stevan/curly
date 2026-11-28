# kind: refused
# perl does not compile it: Missing comma after first argument to warn function (T696).
use v5.42;
my $x = 5;
warn $x -1;
