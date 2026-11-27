# kind: refused
# perl runs it, and says nothing: the piece is read after the sub has stored.
use v5.42;
my $x = 1;
my $r = \$x;
sub set5() {
    $x = 5;
    return 1;
}
my $s = $r->$* . set5();
