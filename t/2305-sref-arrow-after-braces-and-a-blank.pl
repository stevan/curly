# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $a = [1];
my $r = \$a;
say ${ $r } ->[0];
