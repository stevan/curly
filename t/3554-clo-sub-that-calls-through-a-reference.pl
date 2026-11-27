# kind: refused
# perl runs it: '9 0'.
use v5.42;
my $x = 1;
my $bump = sub { $x = 9; return 0 };
sub go() {
    return $bump->();
}
my @l = ($x, go());
say "@l";
