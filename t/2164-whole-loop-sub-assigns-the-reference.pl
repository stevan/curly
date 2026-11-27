# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $r = [1, 2];
sub swap() {
    $r = [7];
    return;
}
for my $x ($r->@*) {
    swap();
}
