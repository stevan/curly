# kind: fault
# model: t/models/clo.py
use v5.42;
no warnings 'recursion';
say(1);
my $deep = sub ($n) { return $n > 50000 ? $n : __SUB__->($n + 1) };
$deep->(0);
say(2);
