# kind: refused
# perl runs it: '9\n'.
use v5.42;
my $x = 1;
my $r = \$x;
sub set9() {
    $x = 9;
    return;
}
for my $v ($r->$*) {
    set9();
    say $v;
}
