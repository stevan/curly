# kind: refused
# perl does not compile it: syntax error (T374).
use v5.42;
my $f = sub { 1 };
say(($f)(1));
