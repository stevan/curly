# kind: fault
# model: t/models/sref.py
use v5.42;
say(1);
my $r;
say(defined($r->$*) ? "d" : "u");
say(2);
