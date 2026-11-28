# t/models/file.py 6459
# kind: fault
use v5.42;
say "before";
open(my $d, '<', '.');
say "not reached";
