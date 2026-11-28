# kind: refused
# perl warns: Found = in conditional, should be == (T676).
use v5.42;
my @a = (1, 2);
$#a = 0 or die "e\n";
