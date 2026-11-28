# kind: refused
# perl returns 0 when the file does not open.
use v5.42;
sub f() {
    open(my $fh, '<', 'in.txt') or return 0;
    return 1;
}
