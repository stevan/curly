use v5.42;
use experimental 'class';
class P { method a { say "first"; 1 } my method say { "mine" } method b { say "second"; 1 } } P->new->a; P->new->b;
