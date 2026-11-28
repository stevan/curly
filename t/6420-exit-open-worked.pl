# t/models/file.py 6420
# kind: warns
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $fh, '<', "in.txt");
say "opened";
die "an open that worked leaves errno 25\n";
