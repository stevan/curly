# t/models/file.py 6440
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
close($fh);
say "closed";
close($fh);
say "not reached";
