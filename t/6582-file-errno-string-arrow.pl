# kind: refused
# perl dies: Can't use string as an ARRAY ref (T689).
use v5.42;
say "why: $!->[0]";
