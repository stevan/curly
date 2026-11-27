# kind: refused
# perl runs it, and warns: Useless use of private variable in void context
use v5.42;
my $r = [1];
my $q = [2];
say "@{$r, $q}";
