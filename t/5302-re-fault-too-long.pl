# kind: fault
# perl's own shortcuts say no at once (T555); the matcher tries every way
# of making sixty a's of a and aa, and stops past its limit (D232).
use v5.42;
my $s = ("a" x 20) . "b";
say $s =~ /^(?:a|aa)*b$/ ? 1 : 0;
$s = ("a" x 60) . "b";
say $s =~ /^(?:a|aa)*$/ ? 1 : 0;
