# kind: refused
# perl does not compile it: syntax error, near "$o isa".
use v5.42;
use experimental 'class';
class A { }
my $o = A->new;
my $x = 2 ge $o isa A;
