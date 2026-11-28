# kind: refused
# perl warns: Non-hex character '-' terminates \x early. Resolved as "\x04-" (T562).
use v5.42;
my $s = "ab";
say $s =~ /\x4-/ ? 1 : 0;
