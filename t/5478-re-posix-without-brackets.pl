# kind: refused
# perl warns: POSIX syntax [: :] belongs inside character classes, and prints 1 (T565).
use v5.42;
my $s = "ab";
say $s =~ /[:alpha:]/ ? 1 : 0;
