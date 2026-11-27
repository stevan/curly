use v5.42;
use experimental 'class';
my $log = "a";
class P { method clone { __CLASS__->new } method v { "c" } }
class Q :isa(P) { ADJUST { $log .= "b" } }
my $q = Q->new;
say $log . "-" . $q->clone->v;
