# kind: refused
# perl runs it: '1'.
use v5.42;
my $r = [1, 2];
my @s;
for my $x ($r->@*) {
    push @s, sub { $x };
}
say $s[0]->();
