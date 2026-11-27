# kind: refused
# perl prints ab-c (R17-07-new-adjust-concat).
use v5.42;
use experimental 'class';
my $log = "a";
class P { ADJUST { $log .= "b" } method v { "c" } }
say $log . "-" . P->new->v;
