# kind: refused
# perl asks of the handle last read (T509).
use v5.42;
my $l = <STDIN>;
say eof ? 1 : 0;
