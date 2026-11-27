# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = "main::x";
$f->();
say(2);
