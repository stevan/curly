use v5.42;
use experimental 'class';
class P { my method join { "mine" } method m { join(",", 1, 2) } } say P->new->m;
