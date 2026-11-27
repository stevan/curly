# kind: refused
# perl runs it: '12'.
use v5.42;
my $n = 2;
my @s;
for my $i (1 .. $n) {
    push @s, sub { $i };
}
say $s[0]->(), $s[1]->();
