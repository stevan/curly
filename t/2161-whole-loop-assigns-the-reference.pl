# kind: refused
# perl runs it: '1\n2\n' over the old array.
use v5.42;
my $r = [1, 2];
for my $x ($r->@*) {
    $r = [7];
    say $x;
}
