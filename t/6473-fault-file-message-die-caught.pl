# t/models/file.py 6473
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
my @l = <$fh>;
say scalar(@l);
try { die "inside" } catch ($e) { say "not reached" }
