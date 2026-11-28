# kind: refused
# perl warns when the file does not open.
use v5.42;
open(my $fh, '<', 'in.txt') or warn "no\n";
