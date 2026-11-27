use v5.42;
use experimental 'class';
class P { method a { $self->&b() } method b { "P.b" } } class Q :isa(P) { method b { "Q.b" } } say Q->new->a; say Q->new->b;
