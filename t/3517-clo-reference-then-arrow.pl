# kind: refused
# perl runs it: 'SCALAR' (T373).
use v5.42;
sub nm() {
    return sub { 42 };
}
my $r = \&nm->();
say ref($r);
