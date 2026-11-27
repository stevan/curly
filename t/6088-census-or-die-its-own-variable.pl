# kind: refused
# perl does not compile it: Global symbol "$f" (the my is declared after the statement).
use v5.42;
my $y = 2;
my $f = $y or die "f is $f\n";
