# kind: fault
# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0 CURLY_HEAP_CAP=8388608
# The matcher's stack is counted against the cap while a match runs
# (D243): a loop of a group is a frame or two a time round, and a million
# times round is more than 8 MB. A run of one character is one frame
# however long (D241), and is in.
use v5.42;
my $s = "ab" x 500000;
say $s =~ /^[ab]*c/ ? 1 : 0;
say $s =~ /^(?:ab)*c/ ? 1 : 0;
