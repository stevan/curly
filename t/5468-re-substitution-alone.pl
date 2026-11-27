# kind: refused
# perl runs it on $_.
use v5.42;
for my $x ("a") {
    my @l = map { s/a/b/r } ($x);
}
