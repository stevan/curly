# t/models/file.py 6432
# kind: warns
# file: in.txt=a\nb\nc\n
use v5.42;
my $tiny = "1e-400" + 0;
say $tiny;
open(my $fh, '<', "in.txt") or die "cannot open in.txt: $!\n";
die "the open set errno after the underflow did\n";
