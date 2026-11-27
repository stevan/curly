# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $h = {};
say(scalar($h->{list}->@*));
say(2);
