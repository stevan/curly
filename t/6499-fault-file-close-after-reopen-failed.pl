# t/models/file.py 6499
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
open($fh, '<', 'nope.txt');
say "before";
close($fh);
