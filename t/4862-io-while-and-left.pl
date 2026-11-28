# kind: refused
# perl warns, and tests the line for truth, with no defined.
use v5.42;
my $l;
while (($l = <STDIN>) && 1) {
    print $l;
}
