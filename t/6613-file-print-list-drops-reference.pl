# kind: refused
# perl writes nothing, and warns: print() on unopened filehandle.
use v5.42;
my $r;
open(my $w, '>', 'o.txt') or die "no\n";
$r = [$w];
$w = undef;
sub clear() {
    $r = undef;
    return 's';
}
print { $r->[0] } 'a', clear();
