# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $x = 1;
my $r = \$x;
my @l = ($r, \$x);
my @s = sort @l;
say(2);
