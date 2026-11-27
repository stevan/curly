# kind: refused
# perl runs it: '1\n' (${$h}{a} is an element of %$h).
use v5.42;
my $h = {a => 1};
say ${ $h }{a};
