# t/models/file.py 6492
# kind: fault
# file: u.txt=caf\0303\0251\n
use v5.42;
open(my $fh, '<', 'u.txt') or die "no\n";
my $l = <$fh>;
say length($l);
print $l;
