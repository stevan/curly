# kind: fault
# perl warns: Argument "abc" isn't numeric in int.
use v5.42;
say int("abc");
