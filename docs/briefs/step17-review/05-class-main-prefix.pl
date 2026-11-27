use v5.42;
use experimental 'class';
class main::P { method v { "ok" } } say P->new->v;
