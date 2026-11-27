# kind: refused
# perl prints ab-c (R17-07-new-field-concat).
use v5.42;
use experimental 'class';
my $log = "a";
class P { field $f = ($log .= "b"); method v { "c" } }
say $log . "-" . P->new->v;
