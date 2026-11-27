# kind: refused
# perl asks eof first, then reads.
use v5.42;
my %h;
$h{eof(STDIN)} = <STDIN>;
