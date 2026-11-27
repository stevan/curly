# kind: refused
# perl warns: matches null string many times (T552).
use v5.42;
my $s = "ab";
say $s =~ /(?:\b)+/ ? 1 : 0;
