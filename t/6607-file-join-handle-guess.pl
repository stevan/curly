# kind: refused
# perl does not compile it: Missing comma after first argument to join or string function.
use v5.42;
my $x = 5;
my $s = join $x -1, 'a', 'b';
