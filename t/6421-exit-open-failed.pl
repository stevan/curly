# t/models/file.py 6421
# kind: warns
use v5.42;
say "before";
open(my $fh, '<', "nope.txt") or die "cannot open nope.txt: $!";
say "not reached";
