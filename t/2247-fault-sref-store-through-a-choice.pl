# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my ($r, $s);
my $c = 1;
${ $c ? $r : $s } = 5;
say(2);
