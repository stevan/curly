# kind: fault
# perl warns: Use of uninitialized value in rand.
use v5.42;
srand(1);
my $u;
say rand($u);
