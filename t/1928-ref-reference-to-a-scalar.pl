# 13a refused this for step 13c, which takes it in.
use v5.42;
my $x = 1;
my $s = \$x;
say ref $s;
