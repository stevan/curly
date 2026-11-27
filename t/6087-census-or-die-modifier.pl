# kind: refused
# perl runs it: the modifier is over the whole.
use v5.42;
my %h = (a => 1);
my $f = $h{a} or die "no\n" if 1;
