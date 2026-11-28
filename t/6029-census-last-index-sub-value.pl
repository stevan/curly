# kind: fault
# perl runs it: '0', the assignment's value.
use v5.42;
my @a = (1, 2);
sub f() {
    $#a = 0;
}
my $v = f();
say $v;
