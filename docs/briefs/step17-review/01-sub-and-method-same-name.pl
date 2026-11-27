use v5.42;
use experimental 'class';
sub v() { "sub" } class P { method v { "meth" } method n { v() } } say P->new->n;
