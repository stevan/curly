# kind: refused
# perl closes the second, and warns: Useless use of private variable in void context.
use v5.42;
open(my $fh, '<', 'in.txt');
my $g = $fh;
close($fh, $g);
