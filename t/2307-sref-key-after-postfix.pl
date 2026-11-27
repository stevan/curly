# kind: refused
# perl does not compile it: syntax error near '$*{'.
use v5.42;
my $h = {a => 1};
my $r = \$h;
say $r->$*{a};
