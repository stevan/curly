# kind: refused
# perl runs it, and says nothing: @a is (2, 3).
use v5.42;
my @a = (1, 2);
my @s;
for my $x (@a) {
    push @s, sub { $x++ };
}
