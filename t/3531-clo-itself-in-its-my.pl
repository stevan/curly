# kind: refused
# perl does not compile it: Global symbol "$f" requires explicit package name (T376).
use v5.42;
my $f = sub { $f->() };
