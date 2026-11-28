# perl prints AB: the case escapes are step 16d's (D120, D256).
use v5.42;
my $x = "ab";
say qq(\U$x);
