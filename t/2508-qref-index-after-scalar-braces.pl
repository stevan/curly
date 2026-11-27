# kind: refused
# perl dies: Not an ARRAY reference
use v5.42;
my $a = [1];
my $s = \$a;
say "${$s}[0]";
