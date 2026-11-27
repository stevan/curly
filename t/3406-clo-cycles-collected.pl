# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0 CURLY_HEAP_CAP=8388608
# Two hundred thousand closures that each hold the variable that holds
# them, dropped as they are made, under a cap of 8 MB (D65, D26, step 14):
# the program ends only if a cycle nothing reaches is freed.
use v5.42;
my $n = 0;
for my $i (1 .. 200000) {
    my $f;
    $f = sub ($k) { return $k ? $f->($k - 1) : $i };
    my @a;
    push @a, sub { scalar(@a) };
    $n += $f->(2) == $i && $a[0]->() == 1 ? 0 : 1;
}
say $n;
