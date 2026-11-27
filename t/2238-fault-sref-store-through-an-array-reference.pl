# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $r = [1];
$r->$* = 5;
say(2);
