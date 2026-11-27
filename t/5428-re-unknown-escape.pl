# kind: refused
# perl warns: Unrecognized escape \y passed through.
use v5.42;
my $s = "ab";
say $s =~ /a\yb/ ? 1 : 0;
