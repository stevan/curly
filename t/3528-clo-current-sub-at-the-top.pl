# kind: refused
# perl runs it: 'u' (undef there).
use v5.42;
say defined(__SUB__) ? "d" : "u";
