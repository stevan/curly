# kind: refused
# perl runs it.
use v5.42;
use experimental 'class';
class P { field $x = 1; method m { for my $x (1, 2) { say $x } return } }
