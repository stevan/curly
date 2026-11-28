# kind: refused
# perl takes '<' for the name, which says to read a file with no name: nothing opens, in silence.
use v5.42;
open(my $fh, '<');
