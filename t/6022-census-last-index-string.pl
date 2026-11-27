# kind: fault
# perl warns: Argument "abc" isn't numeric, and leaves one element.
use v5.42;
my @a = (1, 2, 3);
$#a = "abc";
say scalar @a;
