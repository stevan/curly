# kind: refused
# perl dies: Modification of a read-only value attempted.
use v5.42;
my $v = {k => 1};
sub f() {
    $v = {k => 5};
    return "k";
}
$v->{f()}++;
say $v->{k};
