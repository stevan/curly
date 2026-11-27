# kind: refused
# perl runs it, and says nothing (the last value).
use v5.42;
my $h = {a => 1};
my $x = $h->@{"a"};
