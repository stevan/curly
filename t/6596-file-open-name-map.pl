# kind: refused
# perl opens the file the map gives.
use v5.42;
open(my $fh, '<', map { $_ } 'in.txt');
