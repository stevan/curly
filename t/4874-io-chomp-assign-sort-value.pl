# kind: refused
# perl sorts by what chomp took, 0 each time.
use v5.42;
my @l = sort { chomp(my $x = $a) } 2, 1;
