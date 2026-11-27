use v5.42;
use experimental 'class';
class P { my method length { "mine" } method m { $self->&length() . length("abc") } } say P->new->m;
