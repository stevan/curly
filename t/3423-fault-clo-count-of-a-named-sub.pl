# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
sub one($x) {
    return $x;
}
my $r = \&one;
$r->(1, 2);
say(2);
