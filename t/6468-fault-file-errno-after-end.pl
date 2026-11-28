# t/models/file.py 6468
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt');
open(my $no, '<', 'nope.txt');
my @l = <$fh>;
say scalar(@l);
my $why = $!;
