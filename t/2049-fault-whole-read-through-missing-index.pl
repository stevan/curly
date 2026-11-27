# kind: fault
# model: t/models/whole.py
use v5.42;
say(1);
my @a;
my @x = @{$a[2]};
say(2);
