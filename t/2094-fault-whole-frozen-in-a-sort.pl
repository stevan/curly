# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [2, 1];
my $s = $r;
my @l = sort { push $s->@*, 0; $a <=> $b } $r->@*;
say(2);
