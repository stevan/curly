# kind: fault
# perl warns: Illegal hexadecimal digit 'R' ignored, and prints 10 (D112).
use v5.42;
my $r = [1];
say hex($r);
