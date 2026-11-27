# kind: fault
# model: t/models/qref.py
use v5.42;
say(1);
my $v;
my $r = \$v;
say "<${$r}>";
say(2);
