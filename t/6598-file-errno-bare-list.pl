# kind: refused
# perl reads $! after the call, when die joins its list (T695).
use v5.42;
sub f() {
    return 'x';
}
open(my $fh, '<', 'nope.txt') or die 'no: ', $!, f(), "\n";
