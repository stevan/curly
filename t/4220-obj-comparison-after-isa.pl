# kind: refused
# perl does not compile it: syntax error, near "A <".
use v5.42;
use experimental 'class';
class A { }
my $o = A->new;
my $x = $o isa A < 2;
