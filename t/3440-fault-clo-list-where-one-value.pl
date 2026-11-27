# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my $f = sub { return (1, 2, 3) };
my $c = $f->();
say(2);
