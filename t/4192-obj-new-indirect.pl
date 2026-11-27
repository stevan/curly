# kind: refused
# perl does not compile it (17-indirect): syntax error.
use v5.42;
use experimental 'class';
class P { }
my $p = new P;
