# kind: refused
# perl opens the file, and $ok is 1.
use v5.42;
my $ok = open(my $fh, '<', 'in.txt');
