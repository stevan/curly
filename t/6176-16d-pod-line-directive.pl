# kind: refused
# perl reads the line directive in the POD: 'here at x line 202.' (T667).
use v5.42;
=pod

# line 200 "x"

=cut
die "here";
