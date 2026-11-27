# kind: refused
# perl folds int(3.5) and warns: Found = in conditional (T482).
use v5.42;
my $x;
if ($x = int(3.5)) { say $x }
