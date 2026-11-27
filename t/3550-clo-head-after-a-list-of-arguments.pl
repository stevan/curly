# kind: refused
# perl runs it: '5 2' (T370: the arguments are in place before mk runs).
use v5.42;
my $x = 1;
my @a = (2);
sub mk() {
    $x = 5;
    return sub (@l) { "@l" };
}
say mk()->($x, @a);
