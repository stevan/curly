# kind: refused
# perl prints b-Pb (R17-07-writer-concat).
use v5.42;
use experimental 'class';
class P { field $x :writer = "a"; method go { $x . "-" . ref($self->set_x("b")) . $x } }
