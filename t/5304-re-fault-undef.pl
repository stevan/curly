# kind: fault
# perl warns: Use of uninitialized value $u in pattern match (D48).
use v5.42;
my $u;
say "x" =~ /x/ ? 1 : 0;
say $u =~ /x/ ? 1 : 0;
