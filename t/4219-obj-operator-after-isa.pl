# kind: refused
# perl does not compile it: Bareword "A" not allowed while "strict subs" in use.
use v5.42;
use experimental 'class';
class A { }
my $o = A->new;
say $o isa A - 1;
