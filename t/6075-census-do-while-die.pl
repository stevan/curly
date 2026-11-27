# kind: refused
# perl 5.42 runs it for ever, the block never once (T663).
use v5.42;
my $i = 0;
do {
    $i++;
} while (die "x\n");
