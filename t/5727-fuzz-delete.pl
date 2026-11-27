# kind: refused
# perl dies: Not a HASH reference, of the freed hash.
use v5.42;
my $h = {k => 1};
sub f() {
    $h = {k => 2};
    return "k";
}
delete $h->{f()};
say scalar(%{$h});
