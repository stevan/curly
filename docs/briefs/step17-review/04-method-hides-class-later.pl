use v5.42;
use experimental 'class';
class Q { method m { "q" } } class P { method mk { Q->new->m } method Q { "methQ" } } say P->new->mk;
