# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub { 1 };
say($f < 1 ? "y" : "n");
say(2);
