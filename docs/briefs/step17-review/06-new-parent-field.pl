use v5.42;
use experimental 'class';
my $v = "old";
class A { field $a = ($v = "new"); }
class B :isa(A) { field $x :param :reader; }
say B->new(x => $v)->x;
