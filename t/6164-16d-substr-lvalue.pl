# kind: refused
# perl stores through the substr: 'aZZc' (D254: cut).
use v5.42;
my $s = "abc";
substr($s, 1, 1) = "ZZ";
