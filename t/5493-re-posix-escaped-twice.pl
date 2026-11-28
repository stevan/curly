# kind: refused
# perl warns: POSIX syntax [. .] belongs inside character classes (but this one isn't implemented): an escaped dot ends it (T565).
use v5.42;
my $s = "ab";
say $s =~ /[.\.]/ ? 1 : 0;
