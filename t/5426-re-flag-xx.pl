# kind: refused
# perl runs it: /xx, blanks in classes ignored too.
use v5.42;
my $s = "ab";
say $s =~ /a/xx ? 1 : 0;
