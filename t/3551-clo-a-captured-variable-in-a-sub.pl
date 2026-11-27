# kind: refused
# perl runs it: '5 0' (the closure stores to g's own $n, which the list named first).
use v5.42;
sub g() {
    my $n = 2;
    my $set = sub { $n = 5; return 0 };
    my @l = ($n, $set->());
    return "@l";
}
say g();
