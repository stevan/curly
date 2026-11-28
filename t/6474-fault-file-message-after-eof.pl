# t/models/file.py 6474
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
my $l = <$fh>;
open(my $other, '<', 'in.txt');
my $s = <STDIN>;
say eof($fh) ? "eof" : "more";
warn "w";
