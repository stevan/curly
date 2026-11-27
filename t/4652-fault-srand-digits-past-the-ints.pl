# kind: fault
# perl warns: Integer overflow in srand.
use v5.42;
srand("9223372036854775807");
srand("9223372036854775808");
