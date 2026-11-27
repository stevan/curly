# kind: fault
# model: t/models/clo.py
use v5.42;
say(1);
my @a = (1, 2);
my $f = sub { return @a };
say($f->() + 1);
say(2);
