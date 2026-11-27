# kind: refused
# perl runs it: '1' (the call is of the sub that does not store; D163 asks of every one).
use v5.42;
my $x = 1;
my $bump = sub { $x = 9; return 0 };
my $quiet = sub { 0 };
for my $v ($x) {
    $quiet->();
    say $v;
}
