# kind: fault
# perl dies: not an ARRAY reference. A fault since step 13d, which takes the chain in.
use v5.42;
my $x = 3;
say "@{$x}";
