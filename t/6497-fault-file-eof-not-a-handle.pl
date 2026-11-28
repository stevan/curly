# t/models/file.py 6497
# kind: fault
use v5.42;
my $x = 0;
say "before";
say eof($x) ? "eof" : "more";
