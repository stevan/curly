# kind: refused
# perl dies: Modification of a read-only value attempted (T602).
use v5.42;
my $v;
sub f() {
    $v = undef;
    return "k";
}
$v->{f()} = 5;
say defined($v) ? "def" : "undef";
