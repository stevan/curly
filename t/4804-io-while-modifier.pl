# kind: refused
# perl runs it, and tests the line with defined (T501).
use v5.42;
my $l;
print $l while $l = <STDIN>;
