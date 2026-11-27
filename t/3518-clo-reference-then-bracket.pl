# kind: refused
# perl dies: Too many arguments for subroutine 'main::nm': it calls nm(1).
use v5.42;
sub nm() {
    return sub { 42 };
}
my $r = \&nm(1);
