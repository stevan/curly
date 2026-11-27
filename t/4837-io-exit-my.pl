# kind: refused
# perl does not compile it: Can't modify exit in scalar assignment.
use v5.42;
exit my $x = 3;
