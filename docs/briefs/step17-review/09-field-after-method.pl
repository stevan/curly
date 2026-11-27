use v5.42;
use experimental 'class';
class P { method m { $x } field $x = 1; } say P->new->m;
