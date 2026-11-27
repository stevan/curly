use v5.42;
use experimental 'class';
class Carp { method v { "ok" } } say Carp->new->v;
