# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $x;
my $r = \$x;
push $r->@*, 1;
say(2);
