# t/models/file.py 6452
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
say "before";
printf {$fh} "%d", 1;
