# kind: refused
# perl takes $] for its version, and dies: Unmatched [.
use v5.42;
my $s = "ab";
say $s =~ /[$]/ ? 1 : 0;
