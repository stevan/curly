# t/models/file.py 6472
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', 'in.txt') or die "no\n";
while (my $l = <$fh>) {
    print $l;
    die "bad line" if $l eq "b\n";
}
