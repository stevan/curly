use v5.42;
use experimental 'class';
my $v = "old";
class P { field $a = ($v = "new"); field $x :param :reader; }
say P->new(x => $v)->x;
