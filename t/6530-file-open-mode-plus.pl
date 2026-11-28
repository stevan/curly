# kind: refused
# perl opens the file to read and to write.
use v5.42;
open(my $fh, '+<', 'in.txt');
