# kind: fault
# perl warns: Use of uninitialized value, and makes 'bc'.
use v5.42;
my $s = "abc";
my $u;
substr($s, 0, 1, $u);
say $s;
