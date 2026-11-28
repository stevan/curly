# kind: refused
# perl dies: Can't use an undefined value as filehandle reference.
use v5.42;
my $fh;
open($fh, '<', ($fh = undef) // 'in.txt');
