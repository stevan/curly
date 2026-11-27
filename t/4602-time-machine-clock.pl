# env: CURLY_TIME=0
# kind: new
# With CURLY_TIME at 0 (D63's off) `time` is the machine's clock (D206): a
# whole number past 2026's first second, which is all a test may say of it.
use v5.42;
my $t = time;
say $t > 1767225600 ? "after 2026 began" : "before";
say $t == int($t) ? "whole" : "not";
