# kind: fault
# perl's own shortcuts say no at once (T555). With a backreference in the
# pattern the matcher remembers nothing (D240), tries every way of making
# sixty a's of a and aa, and stops past its limit (D232, D244). Without
# the backreference it says no as perl does.
use v5.42;
my $s = ("a" x 20) . "b";
say $s =~ /^(?:a|aa)*b$/ ? 1 : 0;
$s = ("a" x 60) . "b";
say $s =~ /^(?:a|aa)*$/ ? 1 : 0;
say $s =~ /^(c?)(?:a|aa)*\1c$/ ? 1 : 0;
