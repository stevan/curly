# kind: refused
# perl does not compile it: Experimental keys on scalar is now forbidden.
use v5.42;
my $h = {};
my $r = \$h;
say keys $r->$*;
