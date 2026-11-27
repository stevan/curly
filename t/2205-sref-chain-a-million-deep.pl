# env: CURLY_GC_STRESS=200000
# A chain of a million scalars, each holding a reference to the one made
# before (step 13c): every `my $c` reached again is a new cell (T240), and
# the collector walks the chain with a stack of its own.
use v5.42;
my $r;
for my $i (1 .. 1000000) {
    my $c = $r;
    $r = \$c;
}
my $n = 0;
while (defined($r)) {
    $r = $r->$*;
    $n++;
}
say $n;
