# kind: refused
# perl tests the line for truth, with no defined (T501).
use v5.42;
open(my $fh, '<', 'in.txt');
my $l;
print "x" until $l = <$fh>;
