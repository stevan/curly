# kind: refused
# perl does not compile it: Global symbol @undef requires explicit package name.
use v5.42;
my @c = @{undef};
