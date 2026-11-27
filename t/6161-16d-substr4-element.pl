# kind: refused
# perl changes the element: 'Zb'.
use v5.42;
my @a = ("ab");
substr($a[0], 0, 1, "Z");
