# kind: refused
# perl gives an element of %! (T689).
use v5.42;
say "why: $!{ENOENT}";
