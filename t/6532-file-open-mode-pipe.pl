# kind: refused
# perl runs ls, and reads what it prints.
use v5.42;
open(my $fh, '-|', 'ls');
