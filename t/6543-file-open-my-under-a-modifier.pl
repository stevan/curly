# kind: refused
# perl opens the file when $ok is true, and leaves $fh as it was when it is not.
use v5.42;
my $ok = 1;
open(my $fh, '<', 'in.txt') or die "no\n" if $ok;
