# t/models/file.py 6460
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
say "before";
my $name = "in.txt\0x";
open(my $fh, '<', $name);
