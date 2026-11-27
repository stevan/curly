# kind: refused
# perl warns 'w at FILE line 3.', the line of the last statement the block ran (T316).
use v5.42;
my $i = 0;
do {
    $i++;
} while ($i < 2 && warn "w");
