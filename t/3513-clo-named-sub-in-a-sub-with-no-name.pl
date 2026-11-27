# kind: refused
# perl runs it, and warns of nothing: g is named once, for good (T31).
use v5.42;
my $f = sub {
    sub g() {
        return 1;
    }
    return g();
};
