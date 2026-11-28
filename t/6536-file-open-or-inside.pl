# kind: refused
# perl warns, Useless use of a constant ("<") in void context, and dies: the or takes the whole list for its left side.
use v5.42;
open(my $fh, '<', 'in.txt' or die "x");
