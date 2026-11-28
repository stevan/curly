# kind: refused
# perl warns: Value of <HANDLE> construct can be "0".
use v5.42;
my $l;
my @a = sort { ($l = <STDIN>) && 0 } 1, 2;
