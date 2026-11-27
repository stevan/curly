# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub { 1 };
say(length($f));
say(2);
