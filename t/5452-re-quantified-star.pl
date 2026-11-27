# kind: refused
# perl warns: matches null string many times (T552).
use v5.42;
my $s = "ab";
say $s =~ /(?:a*)*/ ? 1 : 0;
