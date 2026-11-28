# kind: refused
# perl hands the sub $x itself, and reads it after the method stored 5: 5.
use v5.42;
use experimental 'class';
my $x = 1;
sub first(@l) {
    return $l[0];
}
class A { method parts { $x = 5; return (1, 2) } }
say first($x, A->new->parts);
