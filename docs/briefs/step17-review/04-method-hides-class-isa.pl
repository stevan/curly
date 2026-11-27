use v5.42;
use experimental 'class';
class P { method Q { "methQ" } method t($o) { try { return $o isa Q ? 1 : 0 } catch ($e) { return "died: $e" } } } class Q { } print P->new->t(Q->new);
