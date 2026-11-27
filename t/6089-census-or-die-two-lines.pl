# kind: refused
# perl names line 4, the statement's second line: 'x at FILE line 4.' (D150).
use v5.42;
my $y = 1;
my $z = $y - 1
  or die "x";
