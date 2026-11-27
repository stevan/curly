# kind: refused
# perl prints abb-c (R17-07-class-new-subclass): Q's ADJUST runs for __CLASS__->new written in P.
use v5.42;
use experimental 'class';
my $log = "a";
class P { method clone { __CLASS__->new } method v { "c" } }
class Q :isa(P) { ADJUST { $log .= "b" } }
my $q = Q->new;
say $log . "-" . $q->clone->v;
