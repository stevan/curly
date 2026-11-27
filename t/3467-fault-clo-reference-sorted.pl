# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub { 1 };
my @l = ($f, sub { 2 });
my @s = sort @l;
say(2);
