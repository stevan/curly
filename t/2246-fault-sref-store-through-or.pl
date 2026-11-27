# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my ($r, $s);
($r || $s)->$* = 5;
say(2);
