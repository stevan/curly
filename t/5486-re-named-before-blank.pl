# kind: refused
# perl prints 0: the blank after \N{U+41} is skipped, in a class (T567). The compiler printed 1.
use v5.42;
my $s = " ";
say $s =~ /[\N{U+41} ]/x ? 1 : 0;
