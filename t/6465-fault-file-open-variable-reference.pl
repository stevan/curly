# t/models/file.py 6465
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
my $fh = [1];
say "before";
open($fh, '<', 'in.txt');
