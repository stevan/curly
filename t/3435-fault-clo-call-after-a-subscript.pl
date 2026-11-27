# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = [[1]];
$f->[0](1);
say(2);
