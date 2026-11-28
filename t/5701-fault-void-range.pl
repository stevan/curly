# kind: fault
# A sub called for nothing that gives back a range (D245, T600): to perl
# the range is a flip-flop then, which works its left end out and may stop
# there, or compares a constant end with `$.` and warns. A fault, before
# any of it is worked out.
use v5.42;
sub a() { say "a"; return 0 }
sub b() { say "b"; return 3 }
sub f() { return (a() .. b()); }
my @l = f();
say scalar(@l);
f();
say "not reached";
