# kind: refused
# perl reads every line: refused with the rest (D222).
use v5.42;
my @l = (0 || <STDIN>);
