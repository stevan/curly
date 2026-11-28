# kind: refused
# perl warns the same, and prints 1.
use v5.42;
my $s = "ab";
say $s !~ /a/ !~ /1/;
