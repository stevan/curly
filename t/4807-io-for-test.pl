# kind: refused
# perl runs it, and tests the line with defined (T501).
use v5.42;
for (my $i = 0; my $l = <STDIN>; $i++) {
    say $i;
}
