# kind: refused
# perl sorts @x by $by: '1'.
use v5.42;
my @x = (1);
my $by = sub { 0 };
my @s = sort($by @x);
