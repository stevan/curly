# kind: refused
# perl opens the file, and says x.
use v5.42;
open(my $fh, '<', 'in.txt') and print "x\n";
