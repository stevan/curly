# kind: refused
# perl does not compile it: Global symbol "@x" requires explicit package name (did you forget to declare "my @x"?)
use v5.42;
my $r = [1];
say "$r->$#x";
