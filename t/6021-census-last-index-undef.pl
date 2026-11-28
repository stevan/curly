# kind: fault
# perl warns: Use of uninitialized value in scalar assignment, and leaves one element.
use v5.42;
my @a = (1, 2, 3);
my $n;
$#a = $n;
say scalar @a;
