# kind: refused
# perl runs it: '1 2'.
use v5.42;
my $by = sub { $a <=> $b };
my @s = sort $by 2, 1;
say "@s";
