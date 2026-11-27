# kind: refused
# perl runs it, and on an empty stdin prints x without end.
use v5.42;
my $l;
print "x" until $l = <STDIN>;
