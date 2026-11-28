# kind: refused
# perl reads $! after the key is worked out (T695).
use v5.42;
my %h;
open(my $fh, '<', 'nope.txt');
$h{why} = $!;
