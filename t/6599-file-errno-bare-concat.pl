# kind: refused
# perl reads $! as the dot runs.
use v5.42;
open(my $fh, '<', 'nope.txt');
my $s = 'no: ' . $!;
