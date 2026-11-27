# kind: refused
# perl dies: Not a GLOB reference ($f is a file handle there).
use v5.42;
my $f = sub { 1 };
say $f(1);
