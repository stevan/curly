# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub ($x) { if ($x) { return 1; } };
my $v = $f->(0);
say(2);
