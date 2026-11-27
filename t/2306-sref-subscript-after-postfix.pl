# kind: refused
# perl does not compile it: syntax error near '$*['.
use v5.42;
my $a = [1];
my $r = \$a;
say $r->$*[0];
