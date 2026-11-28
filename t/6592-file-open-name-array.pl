# kind: refused
# perl opens the file the array's one element names, and dies of two (T694).
use v5.42;
my @names = ('in.txt');
open(my $fh, '<', @names);
