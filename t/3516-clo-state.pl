# kind: refused
# perl runs it: '121' (T369).
use v5.42;
my @s;
for my $i (1 .. 2) {
    push @s, sub { state $n = 0; return ++$n };
}
