# kind: refused
# perl dies: Invalid [] range, a range from - to the newline (found by briefs/step19-review/patterns.py).
use v5.42;
my $s = "ab";
say $s =~ /[--\n]/ ? 1 : 0;
