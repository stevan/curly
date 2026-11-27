# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my ($r, $s);
my $c = 1;
push @{ $c ? $r : $s }, 1;
say(2);
