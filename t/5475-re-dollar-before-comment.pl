# kind: refused
# perl dies: it reads $#c, the last index of an array @c (T563).
use v5.42;
my $s = "ab";
say $s =~ /b$#c
/x ? 1 : 0;
