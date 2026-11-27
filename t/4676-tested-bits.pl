# kind: refused
# perl folds 1 | 2 and warns: Found = in conditional (T482).
use v5.42;
my $x;
if ($x = 1 | 2) { say $x }
