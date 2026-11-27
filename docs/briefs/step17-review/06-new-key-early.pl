use v5.42;
use experimental 'class';
my $k = "x";
class P { field $a = ($k = "y"); field $x :param :reader = "dx"; field $y :param :reader = "dy"; }
my $p = P->new($k => 5);
say $p->x, " ", $p->y;
