# kind: refused
# perl dies: Unmatched [ (the # after \N{U+41} begins a comment, T567).
use v5.42;
my $s = "ab";
say $s =~ /[\N{U+41}#]/x ? 1 : 0;
