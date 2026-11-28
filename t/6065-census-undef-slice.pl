# kind: refused
# perl makes only the last element undef (T661): '1  3', and a warning.
use v5.42;
my @a = (1, 2, 3);
undef @a[0, 1];
