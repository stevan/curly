# kind: refused
# perl runs it, and tests the line for truth, with no defined (T501).
use v5.42;
my $l;
until ($l = <STDIN>) {
    last;
}
