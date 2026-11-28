# kind: refused
# perl reads the lines after __DATA__: <DATA> is not in the language (D20).
use v5.42;
my @l = <DATA>;
__DATA__
x
