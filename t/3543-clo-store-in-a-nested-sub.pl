# kind: refused
# perl runs it, and says nothing: $a[0] is 5.
use v5.42;
my @a = (1, 2);
my @s;
for my $x (@a) {
    push @s, sub { return sub { $x = 5 } };
}
