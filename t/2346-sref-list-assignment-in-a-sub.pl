# kind: refused
# perl runs it: '51'.
use v5.42;
my $x = 1;
my $r = \$x;
sub swap() {
    (${ $r }, my $z) = (5, 6);
    return 1;
}
say(${ $r }, swap());
