# kind: fault
# the closure over a loop over the array itself freezes it for good (D162): perl pushes.
use v5.42;
my @a = (1);
my @s;
for my $x (@a) {
    push @s, sub { $x };
}
say "made";
push @a, 2;
