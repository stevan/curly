use v5.42;
use experimental 'class';
class P { method trim { "ok" } } say P->new->trim;
