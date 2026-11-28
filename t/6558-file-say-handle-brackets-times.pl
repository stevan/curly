# kind: refused
# perl prints 9 to the file (T684).
use v5.42;
open(my $fh, '>', 'o.txt');
say $fh (1 + 2) * 3;
