# kind: refused
# perl calls f before it reads the line.
use v5.42;
my @a;
sub f() {
    return 0;
}
$a[f()] = <STDIN>;
