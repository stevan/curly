# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub ($x, $y) { $x };
$f->(1);
say(2);
