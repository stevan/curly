# t/models/file.py 6464
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
my $fh = 5;
say "before";
open($fh, '<', 'in.txt');
say "not reached";
