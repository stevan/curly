# kind: refused
# perl dies (17-amp-outside): Undefined subroutine &main::m.
use v5.42;
use experimental 'class';
class P { method m { 1 } }
my $self = P->new;
my $x = $self->&m;
