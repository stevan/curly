# kind: fault
# perl warns of the undef in the sprintf, and dies 'has 1' with no line (E24-die-sprintf); the fault is the undef.
use v5.42;
my $n = 1;
my $u;
say "before";
die sprintf("has %d %s\n", $n, $u)
    if $n;
