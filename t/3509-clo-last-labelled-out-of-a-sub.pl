# kind: refused
# perl runs it: '1', and warns: Exiting subroutine via last.
use v5.42;
LOOP: for my $i (1 .. 2) {
    say $i;
    my $f = sub { last LOOP; };
    $f->();
}
