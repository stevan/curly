# kind: refused
# perl warns: Found = in conditional, should be ==, and dies 'no'.
use v5.42;
my $x = 0 or die "no\n";
