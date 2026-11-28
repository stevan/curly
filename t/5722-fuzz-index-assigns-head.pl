# kind: refused
# perl prints an empty line, and warns: Use of uninitialized value in say.
use v5.42;
my $v = [1, 2];
say $v->[($v = [7, 8]) ? 0 : 1];
