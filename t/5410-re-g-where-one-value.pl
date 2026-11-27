# kind: refused
# perl runs it, and sets pos($s) (T543).
use v5.42;
my $s = "ab";
say(($s =~ /a/g) ? 1 : 0);
