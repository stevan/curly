# kind: fault
# perl warns: Use of uninitialized value in reverse, and prints 'ba'.
use v5.42;
my $u;
say scalar reverse("a", $u, "b");
