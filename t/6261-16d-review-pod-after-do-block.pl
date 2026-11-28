# kind: refused
# perl does not compile it: after the block of a do it looks for an operator (T674).
use v5.42;
my $i = 0;
do { $i++ }
=pod
=cut
until ($i);
say $i;
