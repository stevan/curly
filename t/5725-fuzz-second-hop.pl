# kind: refused
# perl prints an empty line, and warns: Use of uninitialized value in say.
use v5.42;
my $r = [[1]];
sub f() {
    $r->[0] = [5];
    return 0;
}
say $r->[0][f()];
