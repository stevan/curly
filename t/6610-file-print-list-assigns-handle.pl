# kind: refused
# perl writes nothing, and warns: print() on unopened filehandle.
use v5.42;
open(my $w, '>', 'o.txt') or die "no\n";
print $w 'a', ($w = undef) // 'b';
