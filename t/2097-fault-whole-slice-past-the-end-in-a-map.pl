# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1];
my @l = map { $_ } $r->@[2];
say(2);
