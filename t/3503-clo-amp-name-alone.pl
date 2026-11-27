# kind: refused
# perl runs it, and says nothing: g is called with the caller's @_.
use v5.42;
sub g() {
    return 1;
}
&g;
