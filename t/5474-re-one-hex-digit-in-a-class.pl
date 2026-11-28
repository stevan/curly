# kind: refused
# perl warns: Non-hex character ']' terminates \x early (T562).
use v5.42;
my $s = "ab";
say $s =~ /[\x4]/ ? 1 : 0;
