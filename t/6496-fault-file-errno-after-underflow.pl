# t/models/file.py 6496
# kind: fault
use v5.42;
open(my $no, '<', 'nope.txt');
my $tiny = "1e-400" + 0;
say $tiny;
say $!;
