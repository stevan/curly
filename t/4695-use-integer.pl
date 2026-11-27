# kind: refused
# perl makes the bit operators signed, and every arithmetic operator an integer one.
use v5.42;
use integer;
say ~0;
