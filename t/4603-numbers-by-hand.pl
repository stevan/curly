# kind: same
# Step 22 by hand, with perl's answers: the builtins as statements and
# values, with and without brackets, and among other operators.
use v5.42;
srand(11);
rand(10);
srand 12;
rand;
my $first = rand;
srand(12);
rand;
say rand == $first ? "again" : "not";
my $seed = srand();
say $seed == int($seed) && $seed >= 0 ? "a seed" : "none";
say time > 1000000000 ? "the clock" : "not";
my @a = (4, 5, 6);
srand(5);
say $a[rand @a], " ", int(rand(@a)) + 1, " ", int rand 100;
say sqrt(16) + abs(-2) * int(2.9), " ", hex("ff") | oct("0b1") << 8, " ", ~-256 & 0xFF;
my $x = 12;
$x ^= 0b1010;
$x <<= 2;
$x |= 1;
say $x, " ", $x >> 1, " ", -$x & 0xFFFF;
say join ",", map { int sqrt $_ } 1 .. 10;
say join ",", sort { $a <=> $b } map { $_ ^ 5 } 1 .. 8;
say atan2(1, 1) * 4 == 4 * atan2(1, 1) ? "pi" : "not", " ", int(atan2(1, 0) * 2 * 1000000);
sub mask($n, $bits) { return $n & ((1 << $bits) - 1) }
say mask(1000, 4), " ", mask(-1, 16), " ", mask(255, 0);
# perl does not fold rand, srand and time, and is silent of `=` tested
# with one of them on its right (T482).
my $y;
if ($y = rand(1)) { say "a random number" }
if ($y = srand(9)) { say "seeded with $y" }
while (my $t = time) { say "the clock"; last }
