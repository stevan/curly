# kind: refused
# perl reads the key's line first, then the value's (T508).
use v5.42;
my %h;
$h{<STDIN>} = <STDIN>;
