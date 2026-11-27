# kind: refused
# perl runs it: '3'.
use v5.42;
my %h = (add => sub ($x, $y) { $x + $y });
say $h{add} (1, 2);
