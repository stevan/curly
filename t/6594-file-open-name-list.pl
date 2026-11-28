# kind: refused
# perl dies: More than one argument to open(,':perlio').
use v5.42;
open(my $fh, '<', ('a', 'b'));
