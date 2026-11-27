# kind: refused
# perl runs it: '2\n'.
use v5.42;
my $name = 2;
say ${ name };
