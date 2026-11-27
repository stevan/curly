# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $h = {a => [1]};
$h->{a}->$* = 5;
say(2);
