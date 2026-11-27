# kind: refused
# perl does not compile it: Global symbol "$r" requires explicit package name (did you forget to declare "my $r"?)
use v5.42;
my @r = (1);
say "$r->[0]";
