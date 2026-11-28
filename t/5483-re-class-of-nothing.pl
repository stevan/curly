# kind: refused
# perl warns: [^\d\D]* matches null string many times (T566).
use v5.42;
my $s = "ab";
say $s =~ /[^\d\D]*b/ ? 1 : 0;
