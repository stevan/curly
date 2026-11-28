# kind: refused
# perl runs out of memory (T603).
use v5.42;
my $v = 1;
for my $x ($v ? (7) x 1 : 0) {
    say $x;
}
