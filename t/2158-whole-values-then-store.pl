# kind: refused
# perl runs it, and says nothing.
use v5.42;
my $h = {a => 1};
my @l = (values $h->%*, $h->{a} = 9);
