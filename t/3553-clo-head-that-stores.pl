# kind: refused
# perl runs it: '5 0' (the head is worked out after the list's first item is named).
use v5.42;
my $x = 1;
sub mk() {
    $x = 5;
    return sub { 0 };
}
my @l = ($x, mk()->());
say "@l";
