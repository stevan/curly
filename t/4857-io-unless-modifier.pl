# kind: refused
# perl warns: Value of <HANDLE> construct can be "0".
use v5.42;
my $l;
say "end" unless $l = <STDIN>;
