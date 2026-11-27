# kind: refused
# perl runs it, and says nothing: $a[0] is a0, the pieces joined after the index has stored (T230, T238).
use v5.42;
my $r = [3];
my @a;
$a[$r->[0] = 0] = "a$r->[0]";
