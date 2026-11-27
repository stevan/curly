# kind: refused
# perl dies: Modification of a read-only value attempted.
use v5.42;
my $v = [1];
sub f() {
    $v = [2];
    return 0;
}
$v->[f()] .= "x";
say $v->[0];
