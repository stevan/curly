# kind: refused
# perl does not compile it: syntax error near "=" (T673).
use v5.42;
say 1;
=_x
say 2;
=cut
say 3;
