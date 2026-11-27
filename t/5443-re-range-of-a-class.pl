# kind: refused
# perl warns: False [] range.
use v5.42;
my $s = "ab";
say $s =~ /[a-\d]/ ? 1 : 0;
