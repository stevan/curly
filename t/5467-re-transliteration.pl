# kind: refused
# perl runs it: 'bb'.
use v5.42;
my $s = "ab";
$s =~ tr/a/b/;
