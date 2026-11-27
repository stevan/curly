use v5.42;
use experimental 'class';
class P { my method b { "lex" } method b { "pub" } method a { $self->&b() . " " . $self->b } } say P->new->a;
