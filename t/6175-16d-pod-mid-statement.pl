# kind: refused
# perl does not compile it: syntax error near "=".
use v5.42;
say(1,
=pod
x
=cut
2);
