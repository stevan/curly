# kind: refused
# perl opens the file the branch gives, a list as it is.
use v5.42;
my @names = ('in.txt');
open(my $fh, '<', (@names ? @names : 'x'));
