use v5.42;
use experimental 'class';
class Q { method m { "q" } } class P { method Q { "methQ" } method mk { Q->new->m } } say P->new->mk;
