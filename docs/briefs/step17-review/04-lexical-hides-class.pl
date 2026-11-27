use v5.42;
use experimental 'class';
class Q { method m { "q" } } class P { my method Q { "lex" } method mk { Q->new->m } } say P->new->mk;
