# kind: refused
# perl runs it: '1 2 3' (the list holds the array's own elements).
use v5.42;
my @a = (1, 2);
my $r = \@a;
my @l = ($r->@*, push(@a, 3));
