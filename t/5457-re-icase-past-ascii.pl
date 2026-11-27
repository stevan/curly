# kind: refused
# perl runs it, folding by Unicode's tables (T546).
use v5.42;
use utf8;
my $s = "x";
say $s =~ /é/i ? 1 : 0;
