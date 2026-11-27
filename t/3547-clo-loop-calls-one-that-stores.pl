# kind: refused
# perl runs it: '9'.
use v5.42;
my $x = 1;
my $bump = sub { $x = 9; return 0 };
for my $v ($x) {
    $bump->();
    say $v;
}
