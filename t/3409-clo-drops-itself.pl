# env: CURLY_GC_STRESS=1 CURLY_GC_POISON=1
# A closure that drops the last other reference to itself as it runs, and
# then reads what it captured, under a collection at every allocation
# (step 14; T370, D166): the value called is kept in a slot for the whole
# call, and what it captured with it.
use v5.42;
my $keep;
{
    my $n = 5;
    my @a = (1, 2);
    $keep = sub ($m) {
        $keep = undef;
        my @junk = map { [$_] } 1 .. 20;
        return $n * $m + scalar(@a) + scalar(@junk);
    };
}
say $keep->(3), defined($keep) ? " kept" : " dropped";
