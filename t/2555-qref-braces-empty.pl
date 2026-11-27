# kind: refused
# perl does not compile it: syntax error at -e line 2, near "${}"
use v5.42;
say "${}";
