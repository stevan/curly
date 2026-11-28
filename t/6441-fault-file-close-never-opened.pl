# t/models/file.py 6441
# kind: fault
use v5.42;
open(my $fh, '<', 'nope.txt');
say "before";
close($fh);
