# kind: refused
# perl runs it: '9' (T371).
use v5.42;
my ($p, $q, $c) = (1, 2, 1);
my @s;
for my $x ($c ? $p : $q) {
    push @s, sub { $x };
}
$p = 9;
say $s[0]->();
