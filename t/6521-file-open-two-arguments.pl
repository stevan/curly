# kind: refused
# perl opens in.txt to read: the mode is read out of the name (T690).
use v5.42;
open(my $fh, 'in.txt');
