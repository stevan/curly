# kind: fault
# A sub called for nothing that gives back `reverse` (D245): perl joins
# and reverses a string then, and warns of an undef in it. The fault is
# for a `reverse` the call may reach, whichever branch is taken.
use v5.42;
my @a = (1, undef);
sub r($c) { return $c ? 0 : reverse(@a); }
say "before";
r(1);
say "not reached";
