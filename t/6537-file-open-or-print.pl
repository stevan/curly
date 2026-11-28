# kind: refused
# perl opens the file, and prints nothing.
use v5.42;
open(my $fh, '<', 'in.txt') or print "no\n";
