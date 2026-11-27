# kind: refused
# perl takes *2 for a glob, rand's argument (T485).
use v5.42;
my $x = rand * 2;
