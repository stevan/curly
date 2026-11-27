# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0 CURLY_HEAP_CAP=8388608
# Four hundred thousand scalars that each hold a reference to themselves,
# or to another that holds one back, dropped as they are made, under a cap
# of 8 MB (D65, D26, step 13c): the program ends only if a cycle nothing
# reaches is freed.
use v5.42;
my $kept = 0;
for my $i (1 .. 200000) {
    my $c;
    $c = \$c;
    my ($p, $q);
    $p = \$q;
    $q = \$p;
    $kept = $c == $c->$* && ${ ${ $p } } == $p ? $kept : $kept + 1;
}
say $kept;
