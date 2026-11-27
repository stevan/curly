# kind: refused
# perl runs it: '9' (T361).
use v5.42;
my ($p, $q) = (1, 2);
my @s;
for my $x ($p, $q) {
    push @s, sub { $x };
}
$p = 9;
say $s[0]->();
