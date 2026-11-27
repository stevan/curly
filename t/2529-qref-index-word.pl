# kind: refused
# perl does not compile it: Bareword "x" not allowed while "strict subs" in use
use v5.42;
my $r = [1, 2];
say "$r->[x]";
