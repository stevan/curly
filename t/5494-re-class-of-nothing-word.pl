# kind: refused
# perl warns: [^\D\w]+ matches null string many times (T566).
use v5.42;
my $s = "ab";
say $s =~ /[^\D\w]+|b/ ? 1 : 0;
