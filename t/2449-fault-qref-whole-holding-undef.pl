# kind: fault
# model: t/models/qref.py
use v5.42;
say(1);
my $r = [1, undef];
say "<@{$r}>";
say(2);
