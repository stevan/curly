# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $h = {};
say($h->{a}->$*);
say(2);
