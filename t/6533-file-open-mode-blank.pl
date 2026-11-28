# kind: refused
# perl opens the file: a blank after the mode is nothing to it.
use v5.42;
open(my $fh, '< ', 'in.txt');
