# kind: refused
# perl runs it, and says nothing: the piece is read after the sub has stored.
use v5.42;
my $x = 1;
my $bump = sub { $x = 9; return 0 };
my $s = $x . $bump->();
