# kind: refused
# perl runs it, and tests the line with defined.
use v5.42;
my $l;
for (my $i = 0; $l = <STDIN>; $i++) {
    say $i;
}
