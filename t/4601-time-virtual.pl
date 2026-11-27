# kind: new
# The virtual clock (D206): t/knobs.sh sets CURLY_TIME, and `time` is it,
# always, so `time - $t` is 0 however long the program takes. perl's own
# clock is real, so perl is not asked; the answers are by hand.
use v5.42;
say time;
my $t = time;
my $n = 0;
$n += 1 for 1 .. 100000;
say time - $t, " ", $n;
say time() + 1, " ", time / 2, " ", time % 7, " ", int(time / 86400);
