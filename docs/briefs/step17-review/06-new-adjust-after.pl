use v5.42;
use experimental 'class';
my $v = "old";
class P { field $x :param :reader; ADJUST { $v = "new" } }
my $p = P->new(x => $v);
say $p->x, " ", $v;
