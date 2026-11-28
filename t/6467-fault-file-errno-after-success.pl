# t/models/file.py 6467
# kind: fault
# file: in.txt=a\nb\nc\n
use v5.42;
open(my $no, '<', 'nope.txt');
say length("$!") > 0 ? "words" : "none";
open(my $fh, '<', 'in.txt') or die "no\n";
say "why: $!";
