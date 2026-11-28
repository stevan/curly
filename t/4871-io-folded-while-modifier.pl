# kind: refused
# perl tests the line with defined.
use v5.42;
my $l;
print $l while 1 && ($l = <STDIN>);
