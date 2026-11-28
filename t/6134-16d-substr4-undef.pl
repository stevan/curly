# kind: fault
# perl warns: Use of uninitialized value $s in substr, and makes 'x'.
use v5.42;
my $s;
substr($s, 0, 0, "x");
say $s;
