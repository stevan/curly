# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = {a => {}};
my $n = $r->{a}{b}->$#*;
say(2);
