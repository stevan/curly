# t/models/file.py 6454
# kind: fault
use v5.42;
open(my $out, '>', 'o.txt') or die "no\n";
say "before";
say eof($out) ? "eof" : "more";
