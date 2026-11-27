# kind: refused
# perl runs it, and says nothing: $u is never assigned (T198).
use v5.42;
my $r = [3];
my $u;
my $t = "t";
$t .= ($u = "a$r->[0]");
