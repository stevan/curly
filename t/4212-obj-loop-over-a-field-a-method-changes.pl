# kind: refused
# perl's loop walks the field itself, and sees the store.
use v5.42;
use experimental 'class';
class P { field $x = 1; method set { $x = 5; return } method go { for my $v ($x, 2) { $self->set } return } }
