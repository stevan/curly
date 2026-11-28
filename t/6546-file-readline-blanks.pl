# kind: refused
# perl globs: the one name it gives is the handle's address.
use v5.42;
open(my $fh, '<', 'in.txt');
my $l = < $fh >;
