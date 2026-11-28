# t/models/file.py 6470
# kind: fault
use v5.42;
open(my $no, '<', 'nope.txt');
my $why = $!;
say "before";
my $n = $why + 0;
