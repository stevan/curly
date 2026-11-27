# kind: refused
# perl does not compile it: syntax error.
use v5.42;
sub nm() {
    return sub { 42 };
}
my $r = \&nm[0];
