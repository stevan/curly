# kind: refused
# perl opens the file, and says x.
use v5.42;
say "x" if open(my $g, '<', 'in.txt');
