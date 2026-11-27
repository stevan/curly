# kind: refused
# perl takes $b for the variable $b.
use v5.42;
my $s = "ab";
say $s =~ /a$b/ ? 1 : 0;
