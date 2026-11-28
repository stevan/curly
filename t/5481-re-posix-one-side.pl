# kind: refused
# perl warns: POSIX syntax [: :] belongs inside character classes (but this one isn't fully valid) (T565).
use v5.42;
my $s = "ab";
say $s =~ /[:word]/ ? 1 : 0;
