# kind: fault
# perl prints "a" and warns: Use of uninitialized value in join or string (D48).
use v5.42;
my @l = ("a" =~ /(a)(b)?/);
say $l[0];
say $l[1];
