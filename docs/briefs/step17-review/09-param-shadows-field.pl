use v5.42;
use experimental 'class';
class P { field $x = 1; method m($x) { $x } } say P->new->m(5);
