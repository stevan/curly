# kind: refused
# perl reads the key's line first.
use v5.42;
my %h;
$h{<STDIN>} = 1 && <STDIN>;
