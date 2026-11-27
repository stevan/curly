# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my @m = (undef);
my @n = map { $_->$* = 1 } @m;
say(2);
