# kind: refused
# perl runs it: 'undef' (T362).
use v5.42;
my @a = (1, 2);
my @s = map { sub { $_ } } @a;
say defined($s[0]->()) ? "def" : "undef";
