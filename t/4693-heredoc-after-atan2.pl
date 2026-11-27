# kind: refused
# perl looks for a heredoc ended by 1.
use v5.42;
my $x = 3;
say atan2($x <<1, 1);
