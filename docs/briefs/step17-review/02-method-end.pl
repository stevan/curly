use v5.42;
use experimental 'class';
class P { method END { "ok" } method call { $self->END } } say "start"; say P->new->call;
