# t/models/file.py 6444
# kind: fault
use v5.42;
open(my $fh, '<', 'nope.txt');
say "before";
my $l = <$fh>;
