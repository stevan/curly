# kind: refused
# perl prints a to the file.
use v5.42;
open(my $fh, '>', 'o.txt');
print($fh "a");
