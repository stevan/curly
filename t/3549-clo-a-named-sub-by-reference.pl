# kind: refused
# perl runs it: '9'.
use v5.42;
my $x = 1;
sub set9() {
    $x = 9;
    return 0;
}
my $r = \&set9;
for my $v ($x) {
    $r->();
    say $v;
}
