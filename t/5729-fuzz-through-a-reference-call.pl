# kind: refused
# perl prints an empty line, and warns: Use of uninitialized value in say.
use v5.42;
my $v = [1];
my $g = sub { $v = [2]; return 0 };
say $v->[$g->()];
