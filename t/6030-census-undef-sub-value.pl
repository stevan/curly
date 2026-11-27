# kind: fault
# perl runs it: f gives undef, and 'u'.
use v5.42;
my $x = 1;
sub f() {
    undef $x;
}
my $v = f();
say defined $v ? "d" : "u";
