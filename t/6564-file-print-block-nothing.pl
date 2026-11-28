# kind: refused
# perl does not compile it.
use v5.42;
open(my $fh, '>', 'o.txt');
print {$fh};
