# kind: refused
# perl closes the file.
use v5.42;
open(my $fh, '<', 'in.txt');
close $fh, 1;
