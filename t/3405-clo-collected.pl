# env: CURLY_GC_STRESS=20000
# A hundred thousand closures, each the only thing that holds its cell, its
# array or its hash, under the stress knob (step 14; D161): what a closure
# captured lives as long as the closure, and no longer.
use v5.42;
my @keep;
for my $i (1 .. 100000) {
    my $n = $i;
    my @a = ($i);
    my %h = (k => $i);
    my $f = sub { $n + $a[0] + $h{k} };
    push @keep, $f if $i % 10000 == 0;
}
say join(",", map { $_->() } @keep);
# The value called is kept for the whole call: a closure that drops the
# last reference to itself as it runs is not collected under it (T370).
my $self;
$self = sub ($n) {
    $self = undef;
    my @junk = map { [$_] } 1 .. 200;
    return $n . scalar(@junk);
};
say $self->(7);
