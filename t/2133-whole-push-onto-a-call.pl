# kind: refused
# perl does not compile it: Experimental push on scalar is now forbidden.
use v5.42;
sub f() {
    return [];
}
push f(), 1;
