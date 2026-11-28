# kind: refused
# perl warns: POSIX syntax [= =] belongs inside character classes (but this one isn't implemented) (T565).
use v5.42;
my $s = "ab";
say $s =~ /[=a=]/ ? 1 : 0;
