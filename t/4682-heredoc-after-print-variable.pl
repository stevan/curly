# kind: refused
# perl does not compile: Use of bare << to mean <<"" is forbidden (T478).
use v5.42;
my $x = 6;
print $x <<(1);
