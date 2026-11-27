use v5.42;
use experimental 'class';
class P { my method say { "mine" } method m { say "x"; 1 } } P->new->m;
