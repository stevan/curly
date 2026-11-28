# kind: refused
# perl gives the line number of the handle read last.
use v5.42;
open(my $fh, '<', 'in.txt');
my $l = <$fh>;
say $.;
