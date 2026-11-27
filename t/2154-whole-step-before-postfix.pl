# kind: refused
# perl does not compile it: Can't modify array dereference in preincrement (++).
use v5.42;
my $r = [1, 2];
++$r->@*;
