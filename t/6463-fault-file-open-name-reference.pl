# t/models/file.py 6463
# kind: fault
use v5.42;
my $name = ["in.txt"];
say "before";
open(my $fh, '<', $name);
