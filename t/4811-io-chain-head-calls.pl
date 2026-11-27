# kind: refused
# perl calls f before it reads.
use v5.42;
sub f() {
    return [];
}
f()->[0] = <STDIN>;
