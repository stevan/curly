# kind: refused
# perl moves to the start of the file.
use v5.42;
open(my $fh, '<', 'in.txt');
seek($fh, 0, 0);
