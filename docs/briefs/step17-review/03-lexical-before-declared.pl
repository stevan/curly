use v5.42;
use experimental 'class';
class P { method a { $self->&b() } my method b { "b" } } say P->new->a;
