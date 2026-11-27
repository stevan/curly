# kind: refused
# perl prints an empty line, and warns: Use of uninitialized value in say.
use v5.42;
my @a = ([1]);
sub f() {
    @a = ([5]);
    return 0;
}
say $a[0][f()];
