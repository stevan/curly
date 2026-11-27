# kind: refused
# perl does not compile it: Bareword "STDIN" not allowed while strict subs in use.
use v5.42;
my $h = STDIN;
