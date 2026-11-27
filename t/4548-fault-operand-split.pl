# kind: fault
# perl prints 0, or 1 once the string has been used as a float (T475).
use v5.42;
say "0.99999999999999995" | 0;
