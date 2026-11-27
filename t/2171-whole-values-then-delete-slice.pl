# kind: refused
# perl runs it: '3'.
use v5.42;
my $h = {a => 1};
my @l = (values $h->%*, delete $h->@{"a"});
