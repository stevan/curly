# kind: refused
# perl does not compile it: Experimental pop on scalar is now forbidden.
use v5.42;
my $r = [1, 2];
my $x = pop $r->@* + 1;
