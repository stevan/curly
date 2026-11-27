# kind: refused
# perl runs it, prints nothing, and warns twice: Exiting subroutine via next.
use v5.42;
for my $i (1 .. 2) {
    my $f = sub { next; };
    $f->();
    say $i;
}
