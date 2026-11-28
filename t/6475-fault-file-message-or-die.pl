# t/models/file.py 6475
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
my $l = <$fh>;
say "before";
open(my $no, '<', 'nope.txt') or die "cannot open nope.txt: $!";
