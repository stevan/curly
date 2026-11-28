# t/models/file.py 6461
# kind: fault
use v5.42;
use utf8;
say "before";
open(my $fh, '>', 'café.txt');
