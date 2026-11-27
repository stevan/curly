# kind: refused
# perl runs it, and warns: Use of uninitialized value $_.
use v5.42;
my @s;
for (1, 2) {
    push @s, sub { $_ + 1 };
}
say $s[0]->();
