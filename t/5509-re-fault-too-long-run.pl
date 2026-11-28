# kind: fault
# What T568 was, where it is left: a match that fails after a repeat, from
# every start and at every length, with a backreference in the pattern so
# that nothing is remembered (D240). Twelve thousand characters are some
# seventy million steps, and the limit for them is under eleven (D244).
# The same pattern on a tenth of the string is in, and without its
# backreference on all of it.
use v5.42;
my $s = "x" x 1200;
say $s =~ /(y?)x+\1z/ ? 1 : 0;
$s = "x" x 12000;
say $s =~ /x+z/ ? 1 : 0;
say $s =~ /(y?)x+\1z/ ? 1 : 0;
