# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $x = 1;
my $r = \$x;
say(-$r);
say(2);
