# kind: refused
# perl folds the empty string away, and then warns: Value of <HANDLE> construct can be "0".
use v5.42;
my $l;
my $x = "" || ($l = <STDIN>) || 2;
