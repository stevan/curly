use v5.42;
use experimental 'class';
class Q { method m { "q" } } class P { field $Q :reader = 1; method mk { Q->new->m } } say P->new->mk;
