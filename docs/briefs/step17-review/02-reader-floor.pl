use v5.42;
use experimental 'class';
class P { field $floor :reader = 2; } say P->new->floor;
