# kind: refused
# perl prints 2: the 5 goes to the freed array.
use v5.42;
my $v = [1];
sub f() {
    $v = [2];
    return 0;
}
my $z;
($v->[f()], $z) = (5, 6);
say $v->[0];
