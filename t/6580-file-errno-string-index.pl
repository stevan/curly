# kind: refused
# perl gives an element of @!, and warns (T689).
use v5.42;
say "why: $![0]";
