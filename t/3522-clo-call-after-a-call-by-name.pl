# kind: refused
# perl does not compile it: syntax error (T374).
use v5.42;
sub mk2() {
    return sub { 12 };
}
say mk2()();
