# kind: refused
# perl interpolates @a.
use v5.42;
my $s = "ab";
my @a = ("a");
say $s =~ /@a/ ? 1 : 0;
