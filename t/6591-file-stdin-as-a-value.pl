# kind: refused
# perl gives a reference to the glob of stdin.
use v5.42;
my $in = \*STDIN;
