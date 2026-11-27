# kind: refused
# perl folds hex("ff") and warns: Found = in conditional (T482).
use v5.42;
my $x;
while ($x = hex("ff")) { last }
