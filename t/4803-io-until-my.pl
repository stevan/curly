# kind: refused
# perl runs it, and tests the line for truth.
use v5.42;
until (my $l = <STDIN>) {
    last;
}
