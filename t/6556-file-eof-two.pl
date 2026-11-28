# kind: refused
# perl asks of 1, a handle of that name, and warns: Useless use of private variable in void context.
use v5.42;
open(my $fh, '<', 'in.txt');
say eof($fh, 1) ? 1 : 0;
