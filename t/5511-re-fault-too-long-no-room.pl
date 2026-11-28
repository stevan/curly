# kind: fault
# env: CURLY_GC_STRESS=0 CURLY_GC_POISON=0 CURLY_HEAP_CAP=262144
# What the matcher remembers is a bit for each mark of the pattern at each
# byte of the string (D240), counted against the cap (D243). Where there
# is no room for it the matcher goes without, the answer the same: the
# first two matches are short and are in, and the third, which fails
# after a repeat from every start (T568), is past the limit (D244). The
# pattern has some sixty marks, the string 60,000 bytes: 450 KB to
# remember, under a cap of 256 KB.
use v5.42;
my $s = "x" x 60000;
say $s =~ /x+y/ ? 1 : 0;
say $s =~ /^(?:x|y|z){0,60}/ ? 1 : 0;
say $s =~ /^(?:x|y|z){0,60}w/ ? 1 : 0;
say $s =~ /(?:x|y|z){0,60}x+w/ ? 1 : 0;
