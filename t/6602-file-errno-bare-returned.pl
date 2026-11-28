# kind: refused
# perl gives back what $! holds as the sub returns.
use v5.42;
sub why() {
    return $!;
}
