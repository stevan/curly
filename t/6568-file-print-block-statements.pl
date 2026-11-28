# kind: refused
# perl prints a to the file, and warns of the first statement: Useless use of private variable in void context.
use v5.42;
open(my $fh, '>', 'o.txt');
print {$fh; $fh} "a";
