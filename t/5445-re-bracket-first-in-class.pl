# kind: refused
# perl runs it: ] is in the class.
use v5.42;
my $s = "ab";
say $s =~ /[]a]/ ? 1 : 0;
