# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1];
splice($r->@*, 3, 0, 1);
say(2);
