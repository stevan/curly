# kind: refused
# perl runs it: '9\n' (T347).
use v5.42;
my $x = 1;
my $r = \$x;
for my $v (${ $r }) {
    $x = 9;
    say $v;
}
