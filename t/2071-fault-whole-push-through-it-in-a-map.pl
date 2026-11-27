# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my @m = (undef);
my @n = map { push $_->@*, 1 } @m;
say(2);
