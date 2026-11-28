# kind: refused
# perl reads the key's line first, then the value's: the constant is folded away (T519).
use v5.42;
my %h;
$h{<STDIN>} = 1 ? <STDIN> : 2;
