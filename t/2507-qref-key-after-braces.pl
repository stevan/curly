# kind: refused
# perl dies: Not a HASH reference
use v5.42;
my $r = [1];
say "@{$r}{a}";
