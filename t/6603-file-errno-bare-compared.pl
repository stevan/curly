# kind: refused
# perl compares the words, or with == the number.
use v5.42;
open(my $fh, '<', 'nope.txt');
say $! eq 'x' ? 1 : 0;
