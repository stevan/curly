# kind: refused
# perl runs it: '1\n'.
use v5.42;
my $x = 1;
my $r = \$x;
my $y = 2;
for my $v (${ $r }) {
    $r = \$y;
    say $v;
}
