# kind: refused
# perl gives the error's number less one.
use v5.42;
open(my $fh, '<', 'nope.txt');
my $n = $! - 1;
