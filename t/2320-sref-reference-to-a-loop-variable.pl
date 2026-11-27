# kind: refused
# perl runs it, and says nothing: a store through it would change @a (T12).
use v5.42;
my @a = (1, 2);
my @r;
for my $x (@a) {
    push @r, \$x;
}
