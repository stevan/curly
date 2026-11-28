# kind: refused
# perl prints 1 to the file.
use v5.42;
open(my $fh, '>', 'o.txt');
my $f = "%s";
printf $fh $f, 1;
