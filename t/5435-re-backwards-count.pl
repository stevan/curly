# kind: refused
# perl warns: Quantifier {n,m} with n > m can't match.
use v5.42;
my $s = "ab";
say $s =~ /a{2,1}/ ? 1 : 0;
