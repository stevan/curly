# kind: refused
# perl makes $r an array as the loop walks it, and its alias $x sees it: 'd', 'd' (D109: $#{$r} = N may make its head).
use v5.42;
my $r;
for my $x ($r, 1) {
    $#{$r} = 1;
    say defined $x ? "d" : "u";
}
