# kind: fault
# perl warns: Argument "abc" isn't numeric in rand.
use v5.42;
say rand("abc");
