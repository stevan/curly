# kind: refused
# perl runs it: '1\n'.
use v5.42;
sub f() {
    return [1];
}
say "@{f()}";
