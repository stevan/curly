# kind: refused
# perl prints -1 to the file (T684).
use v5.42;
open(my $fh, '>', 'o.txt');
print $fh -1;
