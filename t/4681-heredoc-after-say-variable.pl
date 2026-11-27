# kind: refused
# perl looks for a heredoc ended by 1, and does not compile (T478).
use v5.42;
my $x = 6;
say $x <<1;
