# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my $r = [undef];
say(scalar(keys $r->[0]->%*));
say(2);
