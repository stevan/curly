# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [5];
splice($r->[0]->@*, 0, 0, 1);
say(2);
