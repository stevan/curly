# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [1, 2];
my $s = $r;
my @l = sort { $a <=> $b } grep { push $s->@*, 1 } @{$r};
say(2);
