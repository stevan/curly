# kind: refused
# perl writes nothing to o.txt, and warns: print() on unopened filehandle (T697).
use v5.42;
open(my $w, '>', 'o.txt') or die "no\n";
sub drop() {
    $w = undef;
    return 's';
}
print $w drop(), "t\n";
