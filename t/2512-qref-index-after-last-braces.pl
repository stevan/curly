# kind: refused
# perl does not compile it: syntax error at -e line 3, near "}["
use v5.42;
my $r = [1];
say "$#{$r}[0]";
