# t/models/file.py 6476
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
my $l = <$fh>;
open($fh, '<', 'in.txt');
say "before";
warn "the count of lines goes on";
