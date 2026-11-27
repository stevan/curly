# kind: refused
# perl runs it: '1', and warns: Exiting subroutine via last (T365).
use v5.42;
for my $i (1 .. 2) {
    say $i;
    my $f = sub { last };
    $f->();
}
