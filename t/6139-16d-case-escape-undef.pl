# kind: fault
# perl warns: Use of uninitialized value $x in uc, and prints 'a'.
use v5.42;
my $x;
say "a\U$x";
