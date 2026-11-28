# t/models/file.py 6453
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
say eof($fh) ? "eof" : "more";
close($fh);
say eof($fh) ? "eof" : "more";
