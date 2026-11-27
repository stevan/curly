# kind: refused
# perl calls f and then reads, each time round.
use v5.42;
my @a;
sub f() {
    return 0;
}
while ($a[f()] = <STDIN>) {
    last;
}
