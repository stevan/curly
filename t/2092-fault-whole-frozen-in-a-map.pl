# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1, 2];
my $s = $r;
my @l = map { push $s->@*, 3 } $r->@*;
say(2);
