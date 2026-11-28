# t/models/file.py 6442
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
my $l = <$fh>;
print $l;
close($fh);
$l = <$fh>;
say "not reached";
