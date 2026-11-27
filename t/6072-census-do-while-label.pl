# kind: refused
# perl dies as it runs: Label not found for "last L" (T662).
use v5.42;
my $i = 0;
L: do {
    $i++;
} while ($i < 3);
